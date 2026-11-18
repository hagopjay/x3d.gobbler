"""The spend gate. Nothing calls a model unless HagopJay typed an allowance.

Prices are list prices for Claude Haiku 5.5 from config (source named there).
Every call is estimated before it runs (heuristic input count plus the full
max_tokens output ceiling) and recorded with its actual usage after. This is
not a tokenizer-derived upper bound or an enforceable invoice cap.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import math
from pathlib import Path
import re

_OK = re.compile(r"\s*ok\s*\$?\s*(\d+(?:\.\d+)?)\s*(?:usd)?\s*/\s*(day|d|month|mo)\s*", re.I)


def _number(value, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{label} must be a finite nonnegative number')
    return value


def _tokens(value, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f'{label} must be a nonnegative integer')
    return value


def _time(value: str) -> None:
    if not isinstance(value, str) or datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%dT%H:%M:%SZ') != value:
        raise ValueError('utc must be canonical YYYY-MM-DDTHH:MM:SSZ')


def parse_allowance(comment: str) -> dict | None:
    """'OK $0.03/day' -> {'daily_usd': 0.03}. Anything else -> None. Only the first line counts."""
    first = (comment or "").strip().splitlines()[0] if (comment or "").strip() else ""
    m = _OK.fullmatch(first)
    if not m:
        return None
    amount, unit = float(m.group(1)), m.group(2).lower()
    if not math.isfinite(amount) or amount > 1.0 and unit.startswith("d"):
        return None                     # refuse an implausible daily figure; ask again instead
    return {"daily_usd": amount} if unit.startswith("d") else {"monthly_usd": amount}


@dataclass
class Price:
    input_per_mtok: float
    output_per_mtok: float

    def __post_init__(self):
        _number(self.input_per_mtok, 'input price')
        _number(self.output_per_mtok, 'output price')

    def cost(self, tokens_in: int, tokens_out: int) -> float:
        _tokens(tokens_in, 'input tokens'); _tokens(tokens_out, 'output tokens')
        return _number(tokens_in * self.input_per_mtok / 1e6 + tokens_out * self.output_per_mtok / 1e6, 'usage cost')


def estimate_tokens(text: str) -> int:
    """Rough pre-call estimate: 3.5 characters a token, rounded up. Recorded as an estimate."""
    return max(1, -(-len(text) * 2 // 7))


class Budget:
    def __init__(self, config: dict, allowance: dict, ledger_path: Path, authorized: list[str]):
        llm = config["llm"]
        self.model = llm["model"]
        self.price = Price(llm["price_usd_per_mtok"]["input"], llm["price_usd_per_mtok"]["output"])
        self.price_source = llm["price_source"]
        self.max_tokens = llm["max_tokens"]
        _tokens(self.max_tokens, 'max_tokens')
        if self.max_tokens == 0:
            raise ValueError('max_tokens must be positive')
        self.per_cycle_cap = _number(llm["per_cycle_cap_usd"], 'per-cycle cap')
        self.allowance = dict(allowance)
        for key in ('daily_usd', 'monthly_usd'):
            value = allowance.get(key)
            self.allowance[key] = _number(value if value is not None else 0, key)
        self.authorized = {a.lower() for a in authorized}
        self.path = Path(ledger_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # --- reading the ledger -------------------------------------------------
    def rows(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line.strip()]

    def spent(self, day: str | None = None, month: str | None = None, cycle: int | None = None) -> float:
        total = 0.0
        for r in self.rows():
            if day and not r["utc"].startswith(day):
                continue
            if month and not r["utc"].startswith(month):
                continue
            if cycle is not None and r.get("cycle") != cycle:
                continue
            total += _number(r["actual_usd"], 'ledger actual_usd')
        return total

    # --- the gate -----------------------------------------------------------
    def approved(self) -> bool:
        a = self.allowance
        return isinstance(a.get("approved_by"), str) and a["approved_by"].lower() in self.authorized and \
            (a.get("daily_usd", 0) > 0 or a.get("monthly_usd", 0) > 0)

    def check(self, prompt_chars: int, now_utc: str, cycle: int) -> dict:
        """Decide whether one call may run. Returns the reasoning either way, for the tape."""
        _tokens(prompt_chars, 'prompt_chars'); _tokens(cycle, 'cycle'); _time(now_utc)
        # Compute from the count: no prompt-sized temporary allocation. The
        # tokenizer estimate is explicitly heuristic, not a hard invoice cap.
        est_in = max(1, (prompt_chars * 2 + 6) // 7)
        est = self.price.cost(est_in, self.max_tokens)
        day, month = now_utc[:10], now_utc[:7]
        out = {"model": self.model, "estimate_usd": est, "est_tokens_in": est_in, "est_tokens_out_max": self.max_tokens,
               "price_source": self.price_source}
        if not self.approved():
            return {**out, "allowed": False, "why": "no typed allowance from an authorized human"}
        d, m, c = self.spent(day=day), self.spent(month=month), self.spent(cycle=cycle)
        daily, monthly = self.allowance.get("daily_usd", 0) or 0, self.allowance.get("monthly_usd", 0) or 0
        if daily and d + est > daily:
            return {**out, "allowed": False, "why": f"daily allowance ${daily} would be passed (spent ${d})"}
        if monthly and m + est > monthly:
            return {**out, "allowed": False, "why": f"monthly allowance ${monthly} would be passed (spent ${m})"}
        if c + est > self.per_cycle_cap:
            return {**out, "allowed": False, "why": f"per-cycle cap ${self.per_cycle_cap} would be passed (spent ${c})"}
        return {**out, "allowed": True, "why": f"within allowance: day ${d}+${est} of ${daily or '-'}"}

    def record(self, *, now_utc: str, cycle: int, organ: str, tokens_in: int, tokens_out: int,
               estimate_usd: float, simulated: bool, request_id: str | None = None) -> dict:
        _time(now_utc); _tokens(cycle, 'cycle'); _number(estimate_usd, 'estimate_usd')
        if not isinstance(simulated, bool):
            raise ValueError('simulated must be a boolean')
        actual = self.price.cost(tokens_in, tokens_out)
        if request_id is not None:
            if not isinstance(request_id, str) or not request_id:
                raise ValueError('request_id must be a nonempty string or None')
            for old in self.rows():
                if old.get('request_id') == request_id:
                    identity = ('cycle', 'organ', 'model', 'tokens_in', 'tokens_out', 'simulated')
                    new = dict(cycle=cycle, organ=organ, model=self.model, tokens_in=tokens_in,
                               tokens_out=tokens_out, simulated=simulated)
                    if any(old.get(k) != new[k] for k in identity):
                        raise ValueError('request_id already recorded with different usage identity')
                    return old
        r = {"utc": now_utc, "cycle": cycle, "organ": organ, "model": self.model, "tokens_in": tokens_in,
             "tokens_out": tokens_out, "estimate_usd": estimate_usd, "actual_usd": actual,
             "priced_from": "response.usage x list price" if not simulated else "simulated usage x list price (no API call)",
             "simulated": simulated, "request_id": request_id, "estimate_exceeded": actual > estimate_usd}
        with self.path.open("a") as f:
            f.write(json.dumps(r, sort_keys=True) + "\n")
        return r
