# Gobbler.flyte

One demiurge, four organs, a tight LangGraph loop that turns every 30 minutes. **Scout** watches the X3D web, **Weaver** turns a signal into an x3d.loom action and an X3D candidate, **Witness** referees it with the x3d.accrete gate, the pinned x3d_mcp validator and the loom's trap rules, and **Keeper** commits it to a world that grows by one validated addition per turn. The Gobbler is the graph that holds them. It calls a council after every cycle and asks HagopJay when it should. If he doesn't answer within 4 hours, it takes its own preferred pick, except on anything irreversible.

Design, numbers and limits: [DESIGN.md](DESIGN.md). A simulated day, with its tape, ledgers, world archive and X_ITE stills: [runs/sim-2026-11-18/](runs/sim-2026-11-18/).

## Run it

```bash
cd flyte
pip install -r requirements.txt -r ../../x3d.accrete/requirements.txt   # or set ACCRETE_DIR to an x3d.accrete checkout
python -m unittest discover -s tests            # 14 tests, no network, no API key
python -m gobbler_flyte tick --state state      # one offline tick on the snapshot feeds
python -m gobbler_flyte.sim /tmp/day ../../x3d.loom   # 48 ticks on a simulated clock (about 5 s)
python -m gobbler_flyte answer 7 A --by hagopjay       # local mode: answer a waiting question
pyflyte run flyte_wf.py gobbler_flyte --state_dir $PWD/state   # the same tick as a Flyte workflow (flytekit 1.16.32)
```

## Turn it on (24/7, free)

1. Repository variable `FLYTE_ENABLED` = `true` (Settings > Secrets and variables > Actions > Variables). Until then the cron does nothing.
2. Optional, for model-written fragments: secret `ANTHROPIC_API_KEY` (your Haiku 5.5 key). Then comment `OK $0.03/day` on any `flyte-decision` issue. With no key or no typed OK, every organ runs its deterministic path and spends $0.
3. Answer questions on `flyte-decision` issues with `A`, `B`, `C` or `ok`. An outside send needs `A send`.

## Files

| Path | What |
|---|---|
| `gobbler_flyte/gobbler.py` | the graph: open, scout, weaver, witness, council, ask, wait (`interrupt()`), keeper, close |
| `gobbler_flyte/organs/` | the four organs |
| `gobbler_flyte/runner.py` | one tick: resume answered or timed-out cycles, start a new one, prune finished checkpoints |
| `gobbler_flyte/budget.py`, `llm.py` | the spend gate and the only door to a model (Haiku 5.5 or the scripted FakeLLM) |
| `gobbler_flyte/hitl.py` | GitHub Issues, local files, simulated humans; answer and allowance parsing |
| `gobbler_flyte/relevance.py`, `sources.py` | namesake filter (Ryzen X3D, X3D video net) and feed readers |
| `gobbler_flyte/accrete_bridge.py` | x3d.accrete as referee and memory (nothing re-implemented) |
| `gobbler_flyte/loom/` | hash-pinned copies of x3d.loom `traps.py` and `untrusted.py` |
| `config/flyte.json`, `config/allowance.json` | cadence, humans, timeout, sources, model, prices (zero allowance by default) |
| `fixtures/feeds/` | the 18 Nov 01:46Z snapshot (SHA256 in `SNAPSHOT.sha256`) + 4 labelled SYNTHETIC release rows |
| `flyte_wf.py`, `../.github/workflows/gobbler-flyte.yml` | the two 24/7 hosts |
