"""The Gobbler: one demiurge, the graph that holds the four organs in a tight loop.

    START -> open -> scout --(no signal)--> close -> END
                       |
                       v
                    weaver <--(refused, attempts left)-- witness
                       |                                   ^
                       +-----------------------------------+
                                                           |(pass, or attempts spent)
                                                        council  (the stand-up: every organ reports)
                                     (ask) /    | (proceed)   \\ (hold)
                                        ask     |              close
                                         |      |
                                       wait  (interrupt(): the cycle sleeps until an authorized
                                         |    human answers or the timeout picks for them)
                                         v      v
                                          keeper -> close -> END
"""
from __future__ import annotations

from datetime import datetime, timedelta
from functools import partial

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from .organs.keeper import keeper
from .organs.scout import scout
from .organs.weaver import weaver
from .organs.witness import witness
from .state import FlyteState, row


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def open_cycle(state: dict, ctx) -> dict:
    head = ctx.world.head()["head"] if ctx.world else "n/a"
    allowance = ctx.budget.allowance
    money = (f"allowance ${allowance.get('daily_usd')}/day typed by {allowance.get('approved_by')}" if ctx.budget.approved()
             else "no allowance: deterministic organs only, 0 model calls")
    return {"attempts": 0, "spend": [], "log": [row("gobbler", "open", f"cycle {state['cycle']} at {ctx.now} ({ctx.mode}); "
                                                    f"world head {head}; {money}; {ctx.open_decisions} decision(s) waiting")]}


def council(state: dict, ctx) -> dict:
    w, p = state["witness"], state["proposal"]
    lines = {
        "scout": f"{len(state.get('signals', []))} fresh signal(s), {len(state.get('collisions', []))} namesake(s) set aside",
        "weaver": f"{p['action']} after {state.get('attempts')} attempt(s), prefers {p['preferred']}",
        "witness": f"{w['status']} / {w.get('grade')}",
        "keeper": f"world head {ctx.world.head()['head'] if ctx.world else 'n/a'}, spent today ${ctx.budget.spent(day=ctx.now[:10])}",
    }
    if w["status"] != "pass":
        ruling, why = "hold", "Witness refused every attempt; the refusal itself goes to the ledger as a lesson"
    elif not p["reversible"]:
        ruling, why = "ask", "irreversible option on the table (outside send): a human must answer, no timeout pick"
    elif p["ask_human"] and ctx.open_decisions >= ctx.config["hitl"]["max_open_decisions"]:
        ruling, why = "proceed", f"question queue full ({ctx.open_decisions}); reversible, so the preferred pick goes ahead and is logged"
    elif p["ask_human"] or w.get("grade") == "Suspected":
        ruling, why = "ask", p["ask_reason"]
    else:
        ruling, why = "proceed", f"grade {w.get('grade')}, reversible, nothing to ask"
    return {"council": {"lines": lines, "ruling": ruling, "why": why},
            "log": [row("gobbler", "council", f"stand-up -> {ruling.upper()}: {why}", lines=lines)]}


def ask(state: dict, ctx) -> dict:
    """Write the question into state BEFORE interrupting, so a resume never recomputes the deadline."""
    p = state["proposal"]
    now = datetime.strptime(ctx.now, "%Y-%m-%dT%H:%M:%SZ")
    deadline = now + timedelta(minutes=ctx.config["hitl"]["timeout_minutes"])
    q = {"status": "asked", "cycle": state["cycle"], "asked_utc": ctx.now,
         "deadline_utc": _iso(deadline) if p["reversible"] else None,
         "question": f"Cycle {state['cycle']}: {p['action']} on {p['target']} for \"{p['title']}\"?",
         "options": p["options"], "preferred": p["preferred"], "reversible": p["reversible"],
         "why": state["council"]["why"], "authorized": ctx.config["authorized_humans"]}
    when = f"takes {p['preferred']} at {q['deadline_utc']} if unanswered" if p["reversible"] else "waits for a typed answer, no timeout pick"
    return {"decision": q, "log": [row("gobbler", "ask", f"asked {', '.join(q['authorized'])}: {q['question'][:90]} ({when})", question=q)]}


def wait(state: dict, ctx) -> dict:
    answer = interrupt(state["decision"])           # the cycle sleeps here; the runner resumes it
    d = {**state["decision"], **answer, "status": "answered" if answer.get("by") != "timeout" else "timed-out"}
    text = (f"{answer['by']} picked {answer['choice']} via {answer.get('via')} at {answer.get('utc')}" if answer.get("by") != "timeout"
            else f"no answer by {d['deadline_utc']}: took the preferred pick {answer['choice']}")
    return {"decision": d, "log": [row("gobbler", "decision", text, answer=answer)]}


def close_cycle(state: dict, ctx) -> dict:
    t = state.get("turn") or {}
    if not state.get("signal"):
        text = "nothing new worth a turn"
    elif state.get("council", {}).get("ruling") == "hold":
        text = "held: refusal recorded, no entry"
    else:
        text = (f"turn closed: admitted={t.get('admitted')} drafted={t.get('drafted')} reused=pending "
                f"spend ${t.get('spend_usd', 0)}")
    return {"log": [row("gobbler", "close", text)]}


def after_scout(state: dict) -> str:
    return "weaver" if state.get("signal") else "close"


def after_witness(state: dict, max_attempts: int) -> str:
    if state["witness"]["status"] == "pass" or state.get("attempts", 0) >= max_attempts:
        return "council"
    return "weaver"


def after_council(state: dict) -> str:
    return {"ask": "ask", "proceed": "keeper", "hold": "close"}[state["council"]["ruling"]]


def build(ctx, checkpointer):
    g = StateGraph(FlyteState)
    for name, fn in [("open", open_cycle), ("scout", scout), ("weaver", weaver), ("witness", witness), ("council", council),
                     ("ask", ask), ("wait", wait), ("keeper", keeper), ("close", close_cycle)]:
        g.add_node(name, partial(fn, ctx=ctx))
    g.add_edge(START, "open")
    g.add_edge("open", "scout")
    g.add_conditional_edges("scout", after_scout, {"weaver": "weaver", "close": "close"})
    g.add_edge("weaver", "witness")
    g.add_conditional_edges("witness", partial(after_witness, max_attempts=ctx.config["inner_loop"]["max_weave_attempts"]),
                            {"council": "council", "weaver": "weaver"})
    g.add_conditional_edges("council", after_council, {"ask": "ask", "keeper": "keeper", "close": "close"})
    g.add_edge("ask", "wait")
    g.add_edge("wait", "keeper")
    g.add_edge("keeper", "close")
    g.add_edge("close", END)
    return g.compile(checkpointer=checkpointer, name="gobbler.flyte")
