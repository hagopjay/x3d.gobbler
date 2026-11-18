"""The spend gate. Nothing calls a model unless HagopJay typed an allowance.

Prices are list prices for Claude Haiku 5.5 from config (source named there).
Every call is estimated before it runs (worst case: full max_tokens of output)
and recorded with its actual usage after. Estimates are arithmetic, not invoices.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re

_OK = re.compile(r"^\s*ok\s*\$?\s*(\d+(?:\.\d+)?)\s*(?:usd)?\s*/\s*(day|d|month|mo)\b", re.I)


def parse_allowance(comment: str) -> dict | None:
    """'OK $0.03/day' -> {'daily_usd': 0.03}. Anything else -> None. Only the first line counts."""
    first = (comment or "").strip().splitlines()[0] if (comment or "").strip() else ""
    m = _OK.match(first)
    if not m:
        return None
    amount, unit = float(m.group(1)), m.group(2).lower()
    if amount > 1.0 and unit.startswith("d"):
        return None                     # refuse an implausible daily figure; ask again instead
    return {"daily_usd": amount} if unit.startswith("d") else {"monthly_usd": amount}


@dataclass
class Price:
    input_per_mtok: float
    output_per_mtok: float

    def cost(self, tokens_in: int, tokens_out: int) -> float:
        return tokens_in * self.input_per_mtok / 1e6 + tokens_out * self.output_per_mtok / 1e6


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
        self.per_cycle_cap = llm["per_cycle_cap_usd"]
        self.allowance = allowance
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
            total += r["actual_usd"]
        return round(total, 6)

    # --- the gate -----------------------------------------------------------
    def approved(self) -> bool:
        a = self.allowance
        return bool(a.get("approved_by")) and a["approved_by"].lower() in self.authorized and \
            (a.get("daily_usd", 0) > 0 or a.get("monthly_usd", 0) > 0)

    def check(self, prompt_chars: int, now_utc: str, cycle: int) -> dict:
        """Decide whether one call may run. Returns the reasoning either way, for the tape."""
        est_in = estimate_tokens("x" * prompt_chars)
        est = round(self.price.cost(est_in, self.max_tokens), 6)
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
        actual = round(self.price.cost(tokens_in, tokens_out), 6)
        r = {"utc": now_utc, "cycle": cycle, "organ": organ, "model": self.model, "tokens_in": tokens_in,
             "tokens_out": tokens_out, "estimate_usd": estimate_usd, "actual_usd": actual,
             "priced_from": "response.usage x list price" if not simulated else "simulated usage x list price (no API call)",
             "simulated": simulated, "request_id": request_id}
        with self.path.open("a") as f:
            f.write(json.dumps(r, sort_keys=True) + "\n")
        return r
