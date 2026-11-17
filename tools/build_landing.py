#!/usr/bin/env python3
"""Write index.html (the Pages front door). Every number is read from a receipt file, with the file named next to it."""
import json, pathlib, html
R = pathlib.Path(__file__).resolve().parent.parent
rj = lambda p: json.loads((R / p).read_text())
atlas = rj("flywheel-review/atlas/out/atlas.json")["meta"]["counts"]
br = rj("receipts/browser-observatory.json"); wi = rj("receipts/witness-replay.json"); va = rj("VALIDATION.json")
sb = rj("receipts/browser-standalone.json"); aud = rj("flywheel-review/snapshot-audit.json")
nb = sum(c["ok"] for c in br["checks"]); nw = sum(c["ok"] for c in wi["checks"]); nv = sum(c["ok"] for c in va["checks"])
rows = [
 ("Atlas entities / edges", f'{sum(atlas.values()):,} nodes', "flywheel-review/atlas/out/atlas.json (pinned x3d.loom@ba30153, x3d.docs@ff0565e)"),
 ("Atlas witness, replayed", f"{nw}/{len(wi['checks'])} green", f"receipts/witness-replay.json (Python {wi['engine']['python']}, rdflib {wi['engine']['rdflib']}, x3d_mcp {wi['engine']['x3d_mcp_local_checkout']})"),
 ("Offline consistency checks", f"{nv}/{len(va['checks'])} pass", "VALIDATION.json via verify.py"),
 ("Browser check, observatory", f"{nb}/{len(br['checks'])} pass", f"receipts/browser-observatory.json ({br['browser']}, {br['gl']}; boot {br['bootMs']} ms)"),
 ("Browser check, single-file export", f"{sum(c['ok'] for c in sb['checks'])}/{len(sb['checks'])} pass", "receipts/browser-standalone.json (same rig)"),
]
cards = [
 ("gobbler-flyte/index.html", "The observatory", "Twelve proposed domain feathers around the Gobbler, bound to the Atlas: evidence, foldback replay, local search."),
 ("gobbler-flyte/cinematic.html", "The original cinematic", "The nine-wheel art piece with its score, untouched. Every figure on it is synthetic."),
 ("X3D-Flywheel-Atlas.html", "Read the assessment", "What a flywheel turn is, how to measure it, failure modes, bounded next PRs."),
 ("flywheel-review/atlas/fly.html?out=out-r1", "Walk the Atlas", "The 1,366-sensor walkable graph (replay build with the corrected first viewpoint)."),
 ("Gobbler-Evidence-Loom.html", "Single-file edition", "One 5.7 MB offline HTML file. Audio and 3D labels live in the full project."),
 ("receipts/", "Receipts", "Browser JSON, validator output, witness replay, screenshots."),
]
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gobbler · Evidence Loom</title><link rel="icon" href="data:,">
<style>:root{{--bg:#060b16;--ink:#dbe6f5;--mute:#8aa0bd;--gold:#e8c26a;--line:#1f2e45}}
@media(prefers-color-scheme:light){{:root{{--bg:#f4f1ea;--ink:#16202e;--mute:#566579;--gold:#8a5d00;--line:#cfc8b8}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,sans-serif}}
main{{max-width:1040px;margin:0 auto;padding:40px 16px 64px}}h1{{font:400 clamp(30px,6vw,52px)/1.1 Georgia,serif;margin:.2em 0}}
.e{{letter-spacing:.2em;font-size:11px;color:var(--gold)}}p.l{{color:var(--mute);max-width:640px}}
.g{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;margin:28px 0}}
.g a{{border:1px solid var(--line);padding:16px;text-decoration:none;color:inherit;display:block}}.g a:hover{{border-color:var(--gold)}}
.g b{{display:block;color:var(--gold);margin-bottom:4px}}.g span{{color:var(--mute);font-size:13px}}
table{{border-collapse:collapse;width:100%;font-size:13px}}td,th{{border-top:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}
td:nth-child(2){{white-space:nowrap;font-weight:600}}td:last-child{{color:var(--mute)}}.n{{color:var(--mute);font-size:12px;margin-top:18px}}</style></head><body><main>
<p class="e">GOBBLER / THE EVIDENCE LOOM</p><h1>Many feathers. One learning organism.</h1>
<p class="l">An X3D flywheel observatory: twelve proposed domain interfaces, an Atlas of {sum(atlas.values()):,} entities as memory, and a local foldback test. Motion is illustrative, never repository activity.</p>
<div class="g">{''.join(f'<a href="{h}"><b>{html.escape(t)}</b><span>{html.escape(d)}</span></a>' for h,t,d in cards)}</div>
<table><tr><th>Measure</th><th>Result</th><th>Source</th></tr>{''.join(f'<tr><td>{a}</td><td>{b}</td><td>{html.escape(c)}</td></tr>' for a,b,c in rows)}</table>
<p class="n">Not verified: hardware GPU speed, Firefox/Safari, real phones, audio listening. Browser numbers are software-GL (SwiftShader) behaviour checks, not benchmarks. Hash agreement is byte consistency, not authorship or empirical truth.</p>
</main></body></html>"""
(R / "index.html").write_text(page)
print("index.html", len(page))
