"""The shared state that flows through one Gobbler cycle."""
from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class FlyteState(TypedDict, total=False):
    cycle: int                  # cycle number, also the LangGraph thread suffix
    started_utc: str            # clock value when the cycle began (simulated or real)
    mode: str                   # "live" | "offline" | "sim"
    signals: list[dict]         # Scout output, ranked, already de-duplicated
    collisions: list[dict]      # things that look like X3D but are not (Ryzen X3D, X3D video net)
    signal: dict                # the one signal this cycle works on
    proposal: dict              # Weaver output: action, options, preferred pick, reversibility
    candidate: dict             # X3D fragment candidate for the world (accrete candidate shape)
    witness: dict               # Witness verdict for the latest candidate
    attempts: int               # Weaver<->Witness inner-loop count
    council: dict               # the stand-up: each organ's line plus the Gobbler's ruling
    decision: dict              # human decision record (asked, answered or timed out)
    entry: dict                 # world entry Keeper committed (n, hash, title)
    turn: dict                  # flywheel turn record
    spend: Annotated[list[dict], operator.add]   # every priced call this cycle
    log: Annotated[list[dict], operator.add]     # the run tape: one row per organ action


def row(node: str, kind: str, text: str, **data: Any) -> dict:
    """One line on the run tape."""
    return {"node": node, "kind": kind, "text": text, **({"data": data} if data else {})}
