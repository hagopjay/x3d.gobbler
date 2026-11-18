#!/usr/bin/env python3
"""Execute source-bound local release checks. Native browser acceptance is separate.

Requires tools/requirements-validation.txt and flyte/requirements.txt. Set
GOBBLER_TEST_PYTHON if another interpreter owns those dependencies. An optional
X3D accrete checkout is required to execute the world integration controls; a
skip is explicitly incomplete and never a complete release pass.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = '11a561623b7539f1f9bf20f8ef7bc5b9706c10d2'
RUNTIME_MANIFEST_SHA = '3f045f856842fd0e99047c438eca7b3da3265c71b46f8e954264641410ea1b6d'
IGNORED_DIRS = {'.git', '__pycache__', '.venv', 'node_modules', '.pytest_cache'}
TEST_RUNNER = r'''
import json, pathlib, sys, unittest
suite=unittest.TestLoader().discover(sys.argv[1],pattern='test*.py')
result=unittest.TextTestRunner(verbosity=1).run(suite)
report={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
 'skipped':[{'test':str(t),'reason':reason} for t,reason in result.skipped],
 'expected_failures':len(result.expectedFailures),'unexpected_successes':len(result.unexpectedSuccesses),
 'successful':result.wasSuccessful()}
pathlib.Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
raise SystemExit(0 if result.wasSuccessful() and result.testsRun else 1)
'''
EXTERNAL_RUNNER = r'''
import hashlib,json,os,pathlib,platform,subprocess,sys
from importlib import metadata
root=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(root/'flyte'))
from gobbler_flyte import accrete_bridge
if not accrete_bridge.available():raise RuntimeError('Real x3d.accrete checkout unavailable; set ACCRETE_DIR')
backend=accrete_bridge.ROOT.resolve()
def git(*args):return subprocess.check_output(['git','-C',str(backend),*args],text=True).strip()
files={}
for current,dirs,names in os.walk(backend):
 dirs[:]=sorted(d for d in dirs if d not in {'.git','__pycache__','.venv','node_modules','.pytest_cache'})
 for name in sorted(names):
  p=pathlib.Path(current)/name
  if p.suffix=='.pyc' or p.is_symlink():continue
  files[p.relative_to(backend).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
from accretion.mcp_adapter import instrument_identity
packages=('langgraph','langgraph-checkpoint','langgraph-checkpoint-sqlite','langchain-core','pydantic','lxml','jsonschema','attrs','referencing','rpds-py','jsonschema-specifications')
value={'backend':{'path':str(backend),'commit':git('rev-parse','HEAD'),'working_tree_status':git('status','--porcelain','--untracked-files=all'),'files_sha256':files},
 'bridge_identity':accrete_bridge.identity(),'admission_instrument':instrument_identity(),
 'dependencies':{name:metadata.version(name)for name in packages},'python':platform.python_version(),
 'scope':'Actual external backend, dependency versions and admission instrument used by the integration tests; no hosted model or live send.'}
value['backend']['inventory_sha256']=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
print('__GOBBLER_EXTERNAL_IDENTITY__='+json.dumps(value,sort_keys=True))
'''


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def relative(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def source_inventory():
    files = {}
    for current, directories, names in os.walk(ROOT):
        parent = Path(current)
        directories[:] = sorted(d for d in directories if d not in IGNORED_DIRS)
        rel = parent.relative_to(ROOT).as_posix()
        if rel == 'receipts' or rel.startswith(('receipts/', 'flywheel-review/src/')) or rel == 'flywheel-review/src':
            directories[:] = []
            continue
        for name in sorted(names):
            p = parent / name
            if p.is_symlink() or p.suffix == '.pyc' or name in {'VALIDATION.json', '.standalone-check.html'}:
                continue
            files[p.relative_to(ROOT).as_posix()] = sha(p.read_bytes())
    return {'files_sha256': files, 'inventory_sha256': sha(canonical(files))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'receipts/review-release.json')
    args = parser.parse_args(argv)
    python = os.environ.get('GOBBLER_TEST_PYTHON', sys.executable)
    node = os.environ.get('GOBBLER_TEST_NODE', shutil.which('node') or 'node')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONOPTIMIZE='0')
    report = {'schema': 'gobbler.release-check/1', 'status': 'fail', 'base_commit': BASE,
              'started_utc': datetime.now(timezone.utc).isoformat(),
              'runner_python': platform.python_version(), 'python_command': python, 'node_command': node,
              'scope': 'Executed local controls and byte consistency, not publisher authentication, native browser or GPU acceptance.',
              'checks': [], 'limitations': [
                  'Native browser execution is a separate receipt and is never inferred from these checks.',
                  'A valid X3D document is not evidence of correct scene appearance or scientific claims.',
                  'Authored protocol examples and repository snapshots are not live adoption or a fresh GitHub census.',
                  'This unsigned local report is not a formal Loom acceptance receipt.',
              ]}

    def internal(name, action):
        started = time.perf_counter()
        try:
            detail = action()
            row = {'id': name, 'status': 'pass', 'detail': detail}
        except Exception as error:
            row = {'id': name, 'status': 'fail', 'error': type(error).__name__ + ': ' + str(error)}
        row['elapsed_seconds'] = time.perf_counter() - started
        report['checks'].append(row)
        print(row['status'].upper(), name, flush=True)
        return row

    def command(name, command, timeout=180):
        started = time.perf_counter()
        try:
            done = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
            row = {'id': name, 'argv': list(map(str, command)), 'status': 'pass' if done.returncode == 0 else 'fail',
                   'returncode': done.returncode, 'stdout_sha256': sha(done.stdout.encode()), 'stderr_sha256': sha(done.stderr.encode()),
                   'stdout_tail': done.stdout[-3000:], 'stderr_tail': done.stderr[-3000:]}
        except Exception as error:
            row = {'id': name, 'argv': list(map(str, command)), 'status': 'fail', 'error': type(error).__name__ + ': ' + str(error)}
        row['elapsed_seconds'] = time.perf_counter() - started
        report['checks'].append(row)
        print(row['status'].upper(), name, flush=True)
        return row

    def require(ok, message):
        if not ok:
            raise ValueError(message)

    def runtime_identity():
        raw = (ROOT/'receipts/review-runtime-inventory.json').read_bytes()
        require(sha(raw) == RUNTIME_MANIFEST_SHA, 'Baseline runtime manifest drift')
        origin = json.loads(raw)
        require(origin['base_commit'] == BASE, 'Wrong runtime base')
        expected = origin['files']
        actual = {p.relative_to(ROOT).as_posix() for p in (ROOT/'vendor/x_ite').rglob('*') if p.is_file()}
        require(actual == set(expected), 'Runtime file inventory changed')
        for name, value in expected.items():
            raw = (ROOT/name).read_bytes()
            require(len(raw) == value['bytes'] and sha(raw) == value['sha256'], 'Runtime byte drift: '+name)
        return {'files': len(expected), 'reported_header_version': origin['runtime_reported_header_version'],
                'inventory_sha256': RUNTIME_MANIFEST_SHA, 'scope': origin['scope']}

    def lab_identity():
        raw = (ROOT/'evidence-lab/cases.json').read_bytes()
        cases = json.loads(raw)
        manifest = json.loads((ROOT/'evidence-lab/cases.manifest.json').read_bytes())
        require(manifest['bytes'] == len(raw) and manifest['sha256'] == sha(raw), 'Lab catalog byte drift')
        require(cases['producer_sha256'] == sha((ROOT/'evidence-lab/build_lab.py').read_bytes()), 'Stale lab producer; rebuild first')
        guard = cases['guard']
        require(guard['sha256'] == sha((ROOT/guard['path']).read_bytes()), 'Stale executed guard; rebuild first')
        require(manifest['scene_sha256'] == sha((ROOT/'evidence-lab/instruments.x3d').read_bytes()), 'Stale lab scene')
        for row in cases['fixtures']:
            require(row['sha256'] == sha(row['text'].encode()), 'Damaged saved shader fixture')
        return {'fixtures': len(cases['fixtures']), 'catalog_sha256': manifest['sha256'], 'scene_sha256': manifest['scene_sha256']}

    def external_identity():
        done = subprocess.run([python, '-c', EXTERNAL_RUNNER, str(ROOT)], cwd=ROOT, env=env,
                              capture_output=True, text=True, timeout=60)
        require(done.returncode == 0, 'External accrete identity failed: '+done.stderr[-1500:])
        prefix = '__GOBBLER_EXTERNAL_IDENTITY__='
        rows = [line[len(prefix):] for line in done.stdout.splitlines() if line.startswith(prefix)]
        require(len(rows) == 1, 'External accrete identity output missing/ambiguous')
        return json.loads(rows[0])

    def blender_binding():
        value = json.loads((ROOT/'receipts/review-blender.json').read_bytes())
        require(value['status'] == 'pass' and value['occupancy']['status'] == 'pass', 'Blender import did not pass')
        require(value['tool_sha256'] == sha((ROOT/'tools/render_intervention.py').read_bytes()), 'Stale Blender preview tool')
        require(value['source_sha256'] == sha((ROOT/value['source']).read_bytes()), 'Stale Blender preview source')
        require(value['image_sha256'] == sha((ROOT/'docs/assets/intervention-preview.png').read_bytes()), 'Stale Blender preview image')
        return {'status': 'bound_existing_pass', 'receipt_sha256': sha((ROOT/'receipts/review-blender.json').read_bytes()),
                'scope': 'Existing actual import/render receipt bound to current source, tool and image; Blender was not rerun by this aggregate.'}

    try:
        preflight = command('dependency-preflight', [python, '-c',
            'import lxml.etree,jsonschema,langgraph,langgraph.checkpoint.sqlite;print("validation and workflow dependencies import")'])
        require(preflight['status'] == 'pass', 'Install tools/requirements-validation.txt and flyte/requirements.txt before release checks')
        report['sources_before'] = source_inventory()
        internal('baseline-runtime-identity', runtime_identity)
        internal('lab-producer-and-input-identity', lab_identity)
        report['external_before'] = external_identity()
        report['external_inspector_sha256'] = sha(EXTERNAL_RUNNER.encode())
        with tempfile.TemporaryDirectory(prefix='gobbler-release-') as temporary:
            for optimized in (False, True):
                for name, directory in [('atlas', 'flywheel-review/atlas/tests'), ('tools', 'tools'), ('flyte', 'flyte/tests')]:
                    test_id = name + ('-optimized' if optimized else '-normal')
                    output = Path(temporary)/(test_id+'.json')
                    result = command(test_id, [python, *(['-O'] if optimized else []), '-c', TEST_RUNNER, directory, str(output)])
                    if output.exists():
                        summary = json.loads(output.read_bytes())
                        result['unittest'] = summary
                        if summary['skipped'] or summary['expected_failures'] or summary['unexpected_successes']:
                            result['status'] = 'incomplete'
            command('frontend-controls', [node, '--test', 'tools/observatory-controls.test.mjs'])
            command('intervention-controls', [node, '--test', 'tools/intervention-tests.mjs'])
            command('intervention-ui-controls', [node, '--test', 'tools/intervention-ui.test.mjs'])
            command('browser-http-boundaries', [node, 'tools/browser_check.cjs', '--self-test'])
            command('source-and-generated-consistency', [python, 'verify.py'])
            receipt = ROOT/'receipts/review-x3d.json'
            receipt.unlink(missing_ok=True)
            command('full-pinned-x3d', [python, 'tools/validate_scene.py'])

        def x3d_receipt():
            value = json.loads((ROOT/'receipts/review-x3d.json').read_bytes())
            require(value['status'] == 'pass', 'Full validator did not pass')
            require(value['instrument']['adapter_sha256'] == sha((ROOT/'tools/validate_scene.py').read_bytes()), 'Stale X3D adapter receipt')
            require(len(value['controls']) >= 3 and all(row['caught'] for row in value['controls']), 'Missing negative validator controls')
            for row in value['files']:
                require(row['status'] == 'pass' and row['candidate_sha256'] == sha((ROOT/row['path']).read_bytes()), 'Stale X3D input '+row['path'])
            require(any(row['path'] == 'evidence-lab/instruments.x3d' for row in value['files']), 'Lab escaped full validation')
            return {'documents': len(value['files']), 'negative_controls_caught': len(value['controls']),
                    'receipt_sha256': sha((ROOT/'receipts/review-x3d.json').read_bytes())}
        internal('full-validator-receipt-identity', x3d_receipt)
        internal('blender-source-tool-image-binding', blender_binding)
        report['external_after'] = external_identity()

        def external_stability():
            require(report['external_before'] == report['external_after'], 'External accrete source/commit/dependencies/instrument changed during tests')
            value = report['external_after']
            return {'commit': value['backend']['commit'], 'files': len(value['backend']['files_sha256']),
                    'inventory_sha256': value['backend']['inventory_sha256'], 'working_tree_status': value['backend']['working_tree_status'],
                    'instrument_commit': value['admission_instrument']['commit'], 'dependency_versions': value['dependencies']}
        internal('external-accrete-stability', external_stability)
        report['sources_after'] = source_inventory()

        def source_stability():
            before, after = report['sources_before']['files_sha256'], report['sources_after']['files_sha256']
            changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
            require(not changed, 'Sources changed during verification: '+', '.join(changed))
            return {'files': len(after), 'inventory_sha256': report['sources_after']['inventory_sha256']}
        internal('source-stability', source_stability)
        report['status'] = 'pass' if all(row['status'] == 'pass' for row in report['checks']) else 'incomplete_or_failed'
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        try:
            native = ROOT/'receipts/review-browser.json'
            value = json.loads(native.read_bytes())
            report['native_browser'] = {'status': value['status'], 'created_utc': value.get('started_utc'),
                'receipt_sha256': sha(native.read_bytes()), 'tool_matches_current': value.get('tool_sha256') == sha((ROOT/'tools/browser_check.cjs').read_bytes()),
                'included_in_aggregate': False, 'scope': 'Independent native receipt, not rerun by this aggregate. A blocked launch is not a pass.'}
        except (OSError, ValueError, KeyError) as error:
            report['native_browser'] = {'status': 'not_run', 'included_in_aggregate': False,
                'receipt_error': type(error).__name__+': '+str(error)}
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
        report['tool_sha256'] = sha(Path(__file__).read_bytes())
        report['report_sha256'] = sha(canonical(report))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)+'\n')
        print(json.dumps({'status': report['status'], 'checks': len(report['checks']),
              'failed': [row['id'] for row in report['checks'] if row['status'] != 'pass'], 'output': relative(args.output),
              'native_browser': report['native_browser']['status']}))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
