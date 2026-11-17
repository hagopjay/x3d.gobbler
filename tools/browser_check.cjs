#!/usr/bin/env node
/* Headless-browser check of the observatory: boots the page from a local static server, waits for X3D to load,
 * collects console/page errors, drives the controls, takes screenshots.
 *   node tools/browser_check.cjs [--root DIR] [--page gobbler-flyte/index.html] [--out DIR] [--json FILE]
 * Needs `playwright` resolvable (NODE_PATH) and a Chromium. Software GL: a behaviour and pixel check, NOT a GPU benchmark.
 */
const http = require('http'), fs = require('fs'), path = require('path');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const ROOT = path.resolve(arg('root', path.join(__dirname, '..')));
const PAGE = arg('page', 'gobbler-flyte/index.html');
const OUT = path.resolve(arg('out', path.join(ROOT, 'receipts', 'browser')));
const JSONOUT = arg('json', null);
const ALLOW_ASSETS = process.argv.includes('--allow-missing-assets');   // single-file export: X_ITE's own UI font/logo are not bundled
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.x3d': 'model/x3d+xml', '.wav': 'audio/wav', '.png': 'image/png', '.svg': 'image/svg+xml', '.ttl': 'text/turtle', '.md': 'text/markdown' };
const srv = http.createServer((q, r) => {
  let p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(ROOT)) { r.writeHead(403); return r.end(); }
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html');
  fs.readFile(p, (e, b) => e ? (r.writeHead(404), r.end()) : (r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' }), r.end(b)));
});
(async () => {
  const { chromium } = require('playwright');
  fs.mkdirSync(OUT, { recursive: true });
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const R = { schema: 'gobbler.browser-check/1', page: PAGE, browser: 'Chromium ' + browser.version(), gl: 'software (SwiftShader)', checks: [], consoleErrors: [], pageErrors: [], failedRequests: [] };
  const check = (name, ok, detail) => { R.checks.push({ name, ok: !!ok, ...(detail !== undefined ? { detail } : {}) }); console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail !== undefined ? ' ' + JSON.stringify(detail) : '')); };
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  page.on('console', m => { if (m.type() === 'error') R.consoleErrors.push(m.text().slice(0, 300)); });
  page.on('pageerror', e => R.pageErrors.push(String(e).slice(0, 300)));
  page.on('requestfailed', q => R.failedRequests.push(q.url().replace(/^http:\/\/127\.0\.0\.1:\d+/, '')));
  const t0 = Date.now();
  await page.goto(`http://127.0.0.1:${port}/${PAGE}`, { waitUntil: 'load' });
  const status = async () => (await page.textContent('#load-status')).trim();
  let s = '';
  for (let i = 0; i < 120; i++) { s = await status(); if (!/Opening|Loading/i.test(s)) break; await page.waitForTimeout(500); }
  R.bootMs = Date.now() - t0; R.loadStatus = s;
  check('page boots past "Opening the loom"', !/Opening|Loading/i.test(s), { status: s, ms: R.bootMs });
  const scene = await page.evaluate(() => {
    const c = document.querySelector('x3d-canvas'); const B = c && c.browser; if (!B) return null;
    const w = B.currentScene; return { nodes: w.rootNodes.length, spec: B.getSpecificationVersion ? B.getSpecificationVersion() : null, version: B.getVersion ? B.getVersion() : null };
  });
  check('X3D scene is loaded in X_ITE', scene && scene.nodes > 0, scene);
  const nat = await page.evaluate(() => { const c = document.querySelector('x3d-canvas'); const cv = c.shadowRoot && c.shadowRoot.querySelector('canvas'); return cv ? { w: cv.width, h: cv.height } : null; });
  check('WebGL canvas exists with size', nat && nat.w > 100, nat);
  await page.waitForTimeout(2500);
  await page.screenshot({ path: path.join(OUT, '01-boot.png') });
  const counts = await page.evaluate(() => ({ nodes: document.querySelector('#node-count')?.textContent, edges: document.querySelector('#edge-count')?.textContent, laws: document.querySelector('#law-count')?.textContent, hash: document.querySelector('#hash-state')?.textContent }));
  check('evidence counters filled from Atlas', /2,?181/.test(counts.nodes || '') && /7,?222/.test(counts.edges || ''), counts);
  const feathers = await page.$$('#feathers button');
  check('twelve feather buttons', feathers.length === 12, feathers.length);
  const seen = [];
  for (const i of [0, 5, 11]) { await feathers[i].click(); await page.waitForTimeout(900); seen.push(await page.textContent('#domain-name')); }
  check('feather selection updates dossier', new Set(seen).size === 3, seen);
  await page.screenshot({ path: path.join(OUT, '02-feather.png') });
  await page.click('[data-tab=foldback]'); await page.click('#advance'); await page.waitForTimeout(400);
  const rs = (await page.textContent('#replay-status')).trim();
  check('foldback replay advances', rs.length > 0 && !/^Step through a protocol/.test(rs), rs.slice(0, 100));
  await page.click('[data-tab=search]'); await page.fill('#query', 'fm/1'); await page.waitForTimeout(3000);
  const hits = await page.$$eval('#search-results > *', e => e.length);
  check('Atlas search returns results for fm/1', hits > 0, { hits, state: (await page.textContent('#search-state')).slice(0, 100) });
  await page.screenshot({ path: path.join(OUT, '03-search.png') });
  await page.click('#pause'); check('pause toggles aria-pressed', (await page.getAttribute('#pause', 'aria-pressed')) === 'true');
  await page.click('#close'); await page.waitForTimeout(1500); await page.screenshot({ path: path.join(OUT, '04-loom-heart.png') });
  await page.click('#front'); await page.waitForTimeout(1500);
  const buf = await page.screenshot({ clip: { x: 300, y: 150, width: 840, height: 560 } });
  const distinct = await page.evaluate(async b64 => {
    const im = new Image(); im.src = 'data:image/png;base64,' + b64; await im.decode();
    const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
    const g = c.getContext('2d'); g.drawImage(im, 0, 0); const d = g.getImageData(0, 0, c.width, c.height).data;
    const set = new Set(); for (let i = 0; i < d.length; i += 4 * 97) set.add(((d[i] >> 4) << 8) | ((d[i + 1] >> 4) << 4) | (d[i + 2] >> 4)); return set.size;
  }, buf.toString('base64'));
  check('scene area is not a flat colour', distinct > 40, { distinctQuantisedColours: distinct });
  const fps = await page.evaluate(() => new Promise(r => { let n = 0; const t = performance.now(); const f = () => { n++; if (performance.now() - t > 3000) r(n / 3); else requestAnimationFrame(f); }; requestAnimationFrame(f); }));
  R.cadenceRafPerSecSoftwareGL = +fps.toFixed(1);
  check('page stays live (rAF > 1/s under software GL)', fps > 1, R.cadenceRafPerSecSoftwareGL);
  await page.setViewportSize({ width: 390, height: 844 }); await page.waitForTimeout(1200); await page.screenshot({ path: path.join(OUT, '05-mobile.png') });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  check('mobile width has no horizontal page scroll', overflow <= 1, { overflowPx: overflow });
  const ignorable = e => /favicon|net::ERR_ABORTED/.test(e) || (ALLOW_ASSETS && /Failed to load resource/.test(e));
  if (ALLOW_ASSETS) R.failedRequests = R.failedRequests.filter(u => !/^\/assets\/(fonts|images)\//.test(u));
  check('no uncaught page errors', R.pageErrors.length === 0, R.pageErrors.slice(0, 3));
  check('no console errors', R.consoleErrors.filter(e => !ignorable(e)).length === 0, R.consoleErrors.slice(0, 3));
  check('no failed requests', R.failedRequests.length === 0, R.failedRequests.slice(0, 5));
  R.ok = R.checks.every(c => c.ok);
  if (JSONOUT) fs.writeFileSync(JSONOUT, JSON.stringify(R, null, 1) + '\n');
  await browser.close(); srv.close();
  process.exit(R.ok ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
