"""A simulated day: the real graph, real gate, real validator, real hash chain, on a simulated clock.

What is simulated, and labelled so on the tape:
  - the clock (48 ticks, 30 minutes apart)
  - when each snapshot item "arrives" (its real date if it falls inside the day, else a hash-spread minute)
  - four release rows (fixtures/feeds/synthetic_releases.json), because this container could not read those repos
  - the Haiku replies (FakeLLM: scripted text and usage, priced at list price, no API call)
  - HagopJay (SimHumans: answers the 1st question after 35 min, ignores the 2nd, answers the irreversible one after 6 h ...)
Everything else (Scout's filter, Weaver's playbook, the accrete gate, x3d_mcp XSD + semantic, the SQLite
compare-and-swap world, budget arithmetic, interrupt/resume, timeouts) is the shipped code running for real.
"""
from __future__ import annotations

from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import shutil

from .hitl import SimHumans
from .llm import FakeLLM
from .runner import load_config, tick

# A first try a model plausibly makes (animation nodes nested inside the Group: GATE_CONTAINMENT),
# then the fix, then a texture with a URL (GATE_NODE_FORBIDDEN), then a clean one.
NESTED = ('<Group><Transform DEF="Spin"><Shape><Appearance><Material diffuseColor="0.9 0.6 0.2"/></Appearance>'
          '<Cone bottomRadius="0.6" height="1.6"/></Shape></Transform><TimeSensor DEF="T" cycleInterval="24" loop="true"/>'
          '<OrientationInterpolator DEF="R" key="0 0.5 1" keyValue="0 1 0 0 0 1 0 3.1416 0 1 0 6.2832"/>'
          '<ROUTE fromNode="T" fromField="fraction_changed" toNode="R" toField="set_fraction"/>'
          '<ROUTE fromNode="R" fromField="value_changed" toNode="Spin" toField="set_rotation"/></Group>')
FIXED = ('<Transform DEF="Spin"><Shape><Appearance><Material diffuseColor="0.9 0.6 0.2" emissiveColor="0.2 0.1 0"/></Appearance>'
         '<Cone bottomRadius="0.6" height="1.6"/></Shape><Transform translation="0 1.2 0"><Shape><Appearance>'
         '<PhysicalMaterial baseColor="0.3 0.8 0.9" metallic="0.8" roughness="0.25"/></Appearance><Sphere radius="0.35"/></Shape>'
         '</Transform></Transform><TimeSensor DEF="T" cycleInterval="24" loop="true"/>'
         '<OrientationInterpolator DEF="R" key="0 0.5 1" keyValue="0 1 0 0 0 1 0 3.1416 0 1 0 6.2832"/>'
         '<ROUTE fromNode="T" fromField="fraction_changed" toNode="R" toField="set_fraction"/>'
         '<ROUTE fromNode="R" fromField="value_changed" toNode="Spin" toField="set_rotation"/>')
TEXTURED = ('<Group><Shape><Appearance><ImageTexture url="https://example.com/t.png"/></Appearance><Box size="1 1 1"/></Shape></Group>')
DIAL = ('<Group><Shape><Appearance><Material diffuseColor="0.2 0.5 0.9"/></Appearance><Cylinder radius="0.15" height="2"/></Shape>'
        '<Transform translation="0 1.1 0" rotation="1 0 0 1.5708"><Shape><Appearance><Material diffuseColor="0.95 0.8 0.3" '
        'emissiveColor="0.3 0.25 0.05"/></Appearance><Cylinder radius="0.7" height="0.05"/></Shape></Transform>'
        '<Transform translation="0.7 1.1 0"><Shape><Appearance><Material diffuseColor="0.9 0.3 0.3"/></Appearance>'
        '<Box size="0.2 0.2 0.2"/></Shape></Transform></Group>')
PLAIN = FIXED.replace('<PhysicalMaterial baseColor="0.3 0.8 0.9" metallic="0.8" roughness="0.25"/>',
                      '<Material diffuseColor="0.3 0.8 0.9" specularColor="0.9 0.9 0.9" shininess="0.6"/>')
# PhysicalMaterial passes the accrete gate but the pinned x3d_mcp semantic check refuses it inside accrete's
# profile="Immersive" wrapper (needs component Shape level 2): found by this very loop, see DESIGN.md.
FAKE_SCRIPT = [
    {"text": NESTED, "tokens_in": 2310, "tokens_out": 640},
    {"text": "```xml\n" + FIXED + "\n```", "tokens_in": 2420, "tokens_out": 710},
    {"text": DIAL, "tokens_in": 2350, "tokens_out": 590},
    {"text": PLAIN, "tokens_in": 2300, "tokens_out": 700},
    {"text": TEXTURED, "tokens_in": 2290, "tokens_out": 380},
    {"text": PLAIN, "tokens_in": 2330, "tokens_out": 690},
]
HUMANS = {1: {"after_minutes": 35, "text": "A"},          # 1st question: answers in 35 min, overriding a "B" preference
          2: None, 3: None, 4: None,                      # silence: each times out after 4 h and the preferred pick goes ahead
          5: {"after_minutes": 50, "text": "ok"},         # "ok" = take your preferred pick
          "irreversible": {"after_minutes": 360, "text": "B"}}   # the outside send: no timeout; he answers after 6 h, "note only"


def arrival(item: dict, day0: datetime) -> datetime:
    try:
        p = datetime.strptime(item.get("published", "")[:19], "%Y-%m-%dT%H:%M:%S")
        if day0 <= p < day0 + timedelta(days=1):
            return p
    except ValueError:
        pass
    minute = int(hashlib.sha256(item["id"].encode()).hexdigest()[:6], 16) % 1440
    return day0 + timedelta(minutes=minute)


def run_day(out_dir: Path, start: str = "2026-11-18T00:00:00Z", ticks: int = 48, allowance_usd: float = 0.03,
            loom_dir: str | None = None) -> dict:
    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    config = load_config()
    day0 = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
    fake = FakeLLM(FAKE_SCRIPT)
    humans = SimHumans({k: v for k, v in HUMANS.items() if v},
                       allowance_reply={"daily_usd": allowance_usd, "approved_by": "hagopjay",
                                        "approved_ref": "simulated typed OK", "approved_utc": start})
    summaries = []
    for k in range(ticks):
        now_dt = day0 + timedelta(minutes=30 * k)
        now = now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        summaries.append(tick(out_dir, mode="sim", now=now, config=config, channel=humans, llm_factory=lambda: fake,
                              visible=lambda item, n=now_dt: arrival(item, day0) <= n, loom_dir=loom_dir))
    tape = [json.loads(line) for line in (out_dir / "tape.jsonl").read_text().splitlines()]
    turns = [json.loads(line) for line in (out_dir / "turns.jsonl").read_text().splitlines()] if (out_dir / "turns.jsonl").exists() else []
    spend = [json.loads(line) for line in (out_dir / "spend.jsonl").read_text().splitlines()] if (out_dir / "spend.jsonl").exists() else []
    return {"ticks": ticks, "summaries": summaries, "tape": tape, "turns": turns, "spend": spend}


if __name__ == "__main__":
    import sys
    r = run_day(Path(sys.argv[1] if len(sys.argv) > 1 else "sim-out"), loom_dir=sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps({"ticks": r["ticks"], "rows": len(r["tape"]), "turns": len(r["turns"]),
                      "admitted": sum(t["admitted"] for t in r["turns"]), "spend_usd": round(sum(s["actual_usd"] for s in r["spend"]), 6)}))
