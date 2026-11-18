"""The only door to a model: HagopJay's own Claude Haiku 5.5 key, behind the Budget gate.

`HaikuLLM` calls the Anthropic Messages API. `FakeLLM` returns scripted text and
scripted usage so tests and the simulated day exercise the same path with no call.
Neither is ever constructed unless the Budget says yes for that one call.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Reply:
    text: str
    tokens_in: int
    tokens_out: int
    simulated: bool
    request_id: str | None = None
    stop_reason: str | None = None


class HaikuLLM:
    simulated = False
    def __init__(self, model: str, max_tokens: int, effort: str = "low"):
        import anthropic                     # imported lazily: the default path needs no SDK at all
        self._anthropic = anthropic
        self.client = anthropic.Anthropic()   # resolves ANTHROPIC_API_KEY (an Actions secret he sets)
        self.model, self.max_tokens, self.effort = model, max_tokens, effort

    def complete(self, system: str, prompt: str) -> Reply:
        a = self._anthropic
        try:
            r = self.client.messages.create(
                model=self.model, max_tokens=self.max_tokens,
                output_config={"effort": self.effort},
                system=system, messages=[{"role": "user", "content": prompt}])
        except a.RateLimitError as e:
            raise RuntimeError(f"rate limited: {e.message}") from e
        except a.APIStatusError as e:
            raise RuntimeError(f"API {e.status_code}: {e.message}") from e
        except a.APIConnectionError as e:
            raise RuntimeError("network error reaching the API") from e
        text = "".join(b.text for b in r.content if b.type == "text")
        return Reply(text=text, tokens_in=r.usage.input_tokens, tokens_out=r.usage.output_tokens,
                     simulated=False, request_id=getattr(r, "_request_id", None), stop_reason=r.stop_reason)


class FakeLLM:
    """Scripted replies, in order, cycling. Usage numbers are part of the script."""
    simulated = True

    def __init__(self, script: list[dict]):
        self.script, self.i = script, 0

    def complete(self, system: str, prompt: str) -> Reply:
        s = self.script[self.i % len(self.script)]
        self.i += 1
        return Reply(text=s["text"], tokens_in=s.get("tokens_in", 2400), tokens_out=s.get("tokens_out", 700),
                     simulated=True, stop_reason="end_turn")


def key_present() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
