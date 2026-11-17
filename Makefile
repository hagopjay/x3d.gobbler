# Everything is stdlib Python 3.12+ except where noted. PY can point at a venv that has x3d_mcp's dependencies.
PY ?= python3
.PHONY: test verify pins replay standalone browser sweep all
test:       ; $(PY) -m unittest discover -s flywheel-review/atlas/tests
verify:     ; $(PY) verify.py
pins:       ; $(PY) tools/fetch_pins.py                      # x3d.docs at flywheel-review/atlas/src/DOCS.sha
replay: pins                                                # full Atlas rebuild + witness into out-r1/ (needs rdflib; X3D_MCP_DIR for the scene check)
	mkdir -p flywheel-review/atlas/out-r1
	cd flywheel-review/atlas && ATLAS_OUT=$$PWD/out-r1 $(PY) build_atlas.py >/dev/null && ATLAS_OUT=$$PWD/out-r1 $(PY) fly_atlas.py >/dev/null \
	  && ATLAS_OUT=$$PWD/out-r1 $(PY) check_atlas.py --offline && ATLAS_OUT=$$PWD/out-r1 $(PY) report.py
standalone: ; $(PY) gobbler-flyte/build_standalone.py --output Gobbler-Evidence-Loom.html
browser:    ; node tools/browser_check.cjs --json receipts/browser-observatory.json   # NODE_PATH must reach playwright
sweep:      ; $(PY) tools/leak_sweep.py
all: test verify standalone sweep
