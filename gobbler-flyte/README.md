# Gobbler / The Evidence Loom — new entry point

Open the root `README.md` for launch, rebuild, and evidence limits. `index.html` is now the 12-feather Atlas observatory; `cinematic.html` preserves the original nine-wheel presentation. `build.py`, `scene.x3d`, `data.json`, and music sources remain the original art pipeline. `build_observatory.py` and `observatory.*` form the new evidence view. Use `python3 serve.py` **from the archive root** so that both the demo and Atlas paths resolve.

The historical notes below describe the original artifact and its earlier checks. They are not new rendering or validation results from this iteration.

---

# Gobbler.flyte Mission Control

An art piece, not a dashboard. Nine flywheels (STEM, physics, music, architecture, 3D printing, games, education,
heritage, ontology) ring a fan of light; belts carry pulses from each wheel into the heart.

**Every figure is synthetic.** `data.json` is written by a seeded generator in `build.py` (momentum, turns, worlds,
receipts, spin period). Nothing is read from a repository or measured. The page says so on screen.

```bash
~/Projects/x3d/x3d_mcp/.venv/bin/python build.py     # writes scene.x3d and data.json (deterministic)
python3 -m http.server 8831 --bind 127.0.0.1         # then open http://localhost:8831/
```

- `scene.x3d`: X3D 4.0, Immersive plus Shaders 1 and Shape 5. No Script node. Two GLSL shaders (a nebula sky and a
  floor of rings and nine coloured rays); everything else moves on interpolators. The default viewpoint is a
  96-second looping flight for screen recording.
- `index.html`: X_ITE 16.7.0 (vendored), a title, twelve chips (three views, nine wheels with a ticking synthetic
  counter) and a small card per wheel. Clicking a wheel in the scene does the same as its chip.

Checked on 17 Nov 2026: XSD valid, 0 semantic errors, 0 warnings in the local `x3d_mcp` checkout (`fa0b389`);
opened in X_ITE 16.7.0 in the app's browser pane with no console error; looked at in screenshots from the tour,
the front and above. Not checked: frame rate, other browsers, phones, a real screen recording of the full tour.

Second pass (same day): shockwave rings that cross the floor every 1.6 s, a pulsing beam from the heart into the
sky, a three-ring armillary around the plaza, lightning between neighbouring wheels, four comet swarms, a heart
that cycles through the nine colours, and aurora curtains with a bright core in the sky shader. Re-validated
(XSD valid, 0 errors, 0 warnings) and looked at in two tour screenshots; the lightning flashes are brief and were
not caught in a screenshot.

Soundtrack: `make_music.py` (numpy only) writes `loop.wav`, 96 s at 150 BPM in D minor, one bar per heartbeat
(1.6 s), one chord per shockwave cycle (6.4 s), 60 bars per tour, built in a circular buffer so the loop has no seam
(measured step at the seam 0.006 of full scale; peak -1.0 dBFS, RMS -17 dBFS). The "Sound" button decodes it,
restarts the scene's clocks and starts both together, within roughly a tenth of a second. The owner listened to version 1 on 17 Nov and kept it.

Third pass (17 Nov), at the owner's request:
- **Music v2** (`make_music.py`; v1 kept as `make_music_v1.py`): 160 BPM (v1 was 150, +6.7 %), so a bar is 1.5 s and
  the loop is 90 s. Added a sung lead melody (a four-bar phrase per chord), a harmony a third below from the sixth
  section on, an octave doubling in the climaxes, a slow tenor counter-line, and sevenths and ninths over the pad.
  Levels: peak -1.0 dBFS, RMS -17 dBFS, seam step 0.004. Version 2 has not been listened to by anyone yet.
- **Scene retimed** to the new bar: heartbeat 1.5 s, shockwave cycle 6 s, tour 90 s.
- **Graphics polish**: smoother wheels and rings (finer meshes, a thin outer rim, slimmer spokes), smaller labels,
  finer stars and pulses, a softer four-layer beam, rim lights on the dais, hairline rings and calmer colour on the
  floor, a steadier camera path, and on the page a vignette, letterbox fade, lighter chips and the sound button in
  the chip row.
- **Bug fixed**: starting the sound used `browser.currentTime`, which X_ITE does not have, so the clocks got an
  invalid time and the tour froze while music played (this was also true of the second pass). It now uses the
  system clock; measured after the fix: tour and heartbeat restart together and the camera moves.
