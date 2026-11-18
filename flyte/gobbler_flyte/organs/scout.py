"""Scout: reads every source, throws out namesakes, hands the freshest X3D signal on."""
from __future__ import annotations

from ..loom.untrusted import lint_text
from ..relevance import classify
from ..sources import fetch
from ..state import row


def scout(state: dict, ctx) -> dict:
    per_source, items = [], []
    for src in ctx.sources:
        res = fetch(src, ctx.mode)
        visible = [i for i in res["items"] if ctx.visible(i)]
        per_source.append({"source": src["id"], "status": res["status"], "items": len(visible), "note": res["note"]})
        for it in visible:
            it["trust"] = src.get("trust", "open")
            items.append(it)
    collisions, fresh = [], []
    for it in items:
        c = classify(it["title"] + " " + it.get("summary", ""), it["trust"])
        it.update(label=c["label"], score=round(c["score"], 3), why=c["why"],
                  flags=lint_text(it["title"] + " " + it.get("summary", "")))   # web text is untrusted, always
        if it["id"] in ctx.memory["seen"]:
            continue
        if it["source"] == "loom-commits" and it["title"].startswith("Merge pull request"):
            it.update(label="noise", score=0.0, why=["merge commit: the change itself is its own entry"])
            continue
        if c["label"] in ("amd-x3d", "x3d-video-net"):
            collisions.append(it)
        elif c["label"] in ("x3d", "adjacent") and c["score"] >= ctx.config["scout"]["min_score"]:
            fresh.append(it)
    fresh.sort(key=lambda i: (i["score"], i.get("published", "")), reverse=True)
    fresh = fresh[: ctx.config["scout"]["max_signals_per_tick"]]
    for c in collisions:                      # namesakes are remembered so they are never re-judged
        ctx.memory["seen"].add(c["id"])
    signal = fresh[0] if fresh else None
    if signal:
        ctx.memory["seen"].add(signal["id"])
    flagged = sum(1 for i in items if i.get("flags"))
    counts = {k: sum(1 for i in items if i.get("label") == k) for k in ("x3d", "adjacent", "amd-x3d", "x3d-video-net", "noise")}
    text = (f"{len(items)} items from {sum(1 for p in per_source if p['items'])} live/fixture sources; "
            f"{counts['x3d']} X3D, {counts['adjacent']} adjacent, {counts['amd-x3d']} Ryzen X3D, "
            f"{counts['x3d-video-net']} X3D video net, {counts['noise']} noise; {flagged} injection-linted; {len(fresh)} new")
    log = [row("scout", "sweep", text, per_source=per_source, counts=counts)]
    if collisions:
        log.append(row("scout", "namesake", f"set aside {len(collisions)} namesakes, e.g. \"{collisions[0]['title'][:70]}\"",
                       example=collisions[0]["why"]))
    if signal:
        log.append(row("scout", "signal", f"picked: {signal['title'][:90]} ({signal['source']}, score {signal['score']})",
                       url=signal["url"], why=signal["why"], synthetic=bool(signal.get("synthetic"))))
    return {"signals": fresh, "collisions": collisions[:5], "signal": signal, "log": log}
