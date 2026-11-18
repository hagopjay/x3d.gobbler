# Local verification uses Python3.12+ and Node. Full release also needs the
# declared workflow/validation dependencies and a real x3d.accrete checkout.
PY ?= python3
.PHONY: test verify pins replay standalone browser sweep controls release lab all
test:       ; $(PY) -m unittest discover -s flywheel-review/atlas/tests
verify:     ; $(PY) verify.py
pins:       ; $(PY) tools/fetch_pins.py                      # x3d.docs at flywheel-review/atlas/src/DOCS.sha
replay: pins                                                # full Atlas rebuild + witness into out-r1/ (needs rdflib; X3D_MCP_DIR for the scene check)
	mkdir -p flywheel-review/atlas/out-r1
	cd flywheel-review/atlas && ATLAS_OUT=$$PWD/out-r1 $(PY) build_atlas.py >/dev/null && ATLAS_OUT=$$PWD/out-r1 $(PY) fly_atlas.py >/dev/null \
	  && ATLAS_OUT=$$PWD/out-r1 $(PY) check_atlas.py --offline && ATLAS_OUT=$$PWD/out-r1 $(PY) report.py
standalone: ; $(PY) gobbler-flyte/build_standalone.py --output Gobbler-Evidence-Loom.html
lab:        ; $(PY) evidence-lab/build_lab.py
controls:
	node --test tools/observatory-controls.test.mjs tools/intervention-tests.mjs tools/intervention-ui.test.mjs
release:    ; $(PY) tools/check_release.py
browser:    ; node tools/browser_check.cjs --json receipts/browser-observatory.json   # NODE_PATH must reach playwright
sweep:      ; $(PY) tools/leak_sweep.py
all: standalone verify controls sweep
