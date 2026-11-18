#!/usr/bin/env python3
"""Bundle the new view as one offline HTML file (no audio or 3D font downloads).

This is a convenience export, not a replacement for the fully editable project.
Its domain labels remain in the HTML controls. The original audio stays in ZIP.
"""
from pathlib import Path
import base64
import re
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def encoded(data):
    return base64.b64encode(data).decode('ascii')

def safe_script(text):
    return re.sub(r'</script',r'<\\/script',text,flags=re.IGNORECASE)

def replace_required(text, old, new, *, label=None):
    """A changed template must fail the export instead of shipping half a shim."""
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Standalone contract {label or old[:70]!r}: expected one anchor, got {count}")
    return text.replace(old, new, 1)


def build(output):
    html=(HERE/'index.html').read_text()
    css=(HERE/'observatory.css').read_text()+'\n'+(ROOT/'vendor/x_ite/x_ite.css').read_text()
    # The inline copy of x_ite.css resolves url(assets/...) against the page, so a single file asked its own
    # origin for /assets/images/logo.svg and the PT Sans font (two 404s on a native run, 18 Nov). Inline them.
    # The SRI-pinned blob copy below stays byte-exact.
    import base64 as _b64, mimetypes as _mt
    def _inline_asset(m):
        f=ROOT/'vendor/x_ite'/m.group(2)
        if not f.is_file():
            raise ValueError(f'x_ite.css references a missing asset: {m.group(2)}')
        mime={'.svg':'image/svg+xml','.woff2':'font/woff2'}.get(f.suffix) or _mt.guess_type(f.name)[0] or 'application/octet-stream'
        return 'url('+m.group(1)+'data:'+mime+';base64,'+_b64.b64encode(f.read_bytes()).decode()+m.group(1)+')'
    css=re.sub(r'url\((["\']?)(assets/[^)"\']+)\1\)',_inline_asset,css)
    js=(HERE/'observatory.js').read_text()
    engine=(ROOT/'vendor/x_ite/x_ite.min.js').read_text()
    # The supplied runtime uses nullish fallback for currentScript.src. Inline
    # scripts expose an empty string, so use location as their valid asset base.
    marker='document.currentScript?.src??document.location.href'
    if engine.count(marker)!=1:
        raise ValueError('Bundled runtime changed: recheck the inline asset-base shim')
    engine=engine.replace(marker,'(document.currentScript?.src||document.location.href)')
    # X_ITE lazy-loads each component it needs by import()-ing assets/components/<Name>Component[.min].js resolved against
    # its own script URL. A single file has no such folder. Found by running the export in Chromium: it stopped at
    # "Could not open the X3D loom" with five 404-style component requests. Fix: embed the five components the scene
    # touches, turn them into blob: URLs at start-up, and make getProviderURL() return those instead.
    COMPONENTS=['EventUtilities','Geometry2D','KeyDeviceSensor','Scripting','Text']
    provider_marker='getProviderURL(e){if(!e)return"https://create3000.github.io/x_ite/";'
    if engine.count(provider_marker)!=1:
        raise ValueError('Bundled runtime changed: recheck the getProviderURL() shim')
    engine=engine.replace(provider_marker,provider_marker+'if(globalThis.__x3dComponents?.[e])return globalThis.__x3dComponents[e];')
    import json
    import re as _re, base64 as _b64
    lib_marker='getLibraryURL(e){return new URL('
    css_pat=r'i\.href=new URL\("x_ite\.css",([^)]*\))\)'
    if engine.count(lib_marker)!=1 or len(_re.findall(css_pat,engine))!=1:
        raise ValueError('Bundled runtime changed: recheck the getLibraryURL()/x_ite.css shims')
    engine=engine.replace(lib_marker,'getLibraryURL(e){if(globalThis.__x3dLibs?.[e])return globalThis.__x3dLibs[e];return new URL(')
    # X_ITE registers its PT Sans faces through getFontsURL(), again relative to its script URL (a 404 per face).
    fonts_marker='getFontsURL(e){return new URL('
    if engine.count(fonts_marker)!=1:
        raise ValueError('Bundled runtime changed: recheck the getFontsURL() shim')
    engine=engine.replace(fonts_marker,'getFontsURL(e){if(globalThis.__x3dFonts?.[e])return globalThis.__x3dFonts[e];return new URL(')
    FONTS=['PT_Sans/PTSans-Regular.woff2','PT_Sans/PTSans-Bold.woff2','PT_Sans/PTSans-Italic.woff2']
    for f in FONTS:
        if engine.count('fp("'+f+'"')!=1:
            raise ValueError(f'Bundled runtime changed: font {f} is no longer registered')
    # the browser keeps itself hidden until its stylesheet <link> loads, so a failed x_ite.css request means a blank canvas
    engine=_re.sub(css_pat,r'i.href=globalThis.__x3dCssURL||new URL("x_ite.css",\1)',engine)
    wasm=_b64.b64encode((ROOT/'vendor/x_ite/assets/lib/mikktspace_bg.wasm').read_bytes()).decode()
    # The engine pins x_ite.css with an SRI hash. Its url(assets/...) references resolve against the page in a
    # single file, so the served copy inlines them as data: URIs and the pinned hash is replaced by the sha384 of
    # exactly those served bytes (the original hash must still be present once, or the build fails).
    import hashlib as _hl
    css_raw=(ROOT/'vendor/x_ite/x_ite.css').read_bytes()
    sri_old='sha384-'+_b64.b64encode(_hl.sha384(css_raw).digest()).decode()
    if engine.count('i.integrity="'+sri_old+'"')!=1:
        raise ValueError('Bundled runtime changed: the x_ite.css SRI pin no longer matches the vendored stylesheet')
    css_exact=re.sub(r'url\((["\']?)(assets/[^)"\']+)\1\)',_inline_asset,css_raw.decode('utf-8'))
    sri_new='sha384-'+_b64.b64encode(_hl.sha384(css_exact.encode('utf-8')).digest()).decode()
    engine=engine.replace('i.integrity="'+sri_old+'"','i.integrity="'+sri_new+'"',1)
    comp_src={c:(ROOT/f'vendor/x_ite/assets/components/{c}Component.min.js').read_text() for c in COMPONENTS}
    text_component=('globalThis.__x3dComponents=Object.fromEntries(Object.entries('+json.dumps(comp_src).replace('</','<\\/')+
                    ').map(([k,v])=>[k,URL.createObjectURL(new Blob([v],{type:"text/javascript"}))]));'
                    +'globalThis.__x3dLibs={"mikktspace_bg.wasm":"data:application/wasm;base64,'+wasm+'"};'
                    +'globalThis.__x3dFonts='+json.dumps({f:'data:font/woff2;base64,'+_b64.b64encode((ROOT/'vendor/x_ite/assets/fonts'/f).read_bytes()).decode() for f in FONTS})+';'
                    +'globalThis.__x3dCssURL=URL.createObjectURL(new Blob(['+json.dumps(css_exact).replace('</','<\\/')+'],{type:"text/css"}));')
    # Font-independent export: all domain names remain available in accessible HTML.
    tree=ET.fromstring((HERE/'observatory.x3d').read_text())
    for parent in tree.iter():
        for child in list(parent):
            if child.tag=='Shape' and child.find('Text') is not None:
                parent.remove(child)
    scene=ET.tostring(tree,encoding='utf-8')
    blobs={'embedded-data':(HERE/'observatory.json').read_bytes(),
           'embedded-atlas':(ROOT/'flywheel-review/atlas/out/atlas.json').read_bytes(),
           'embedded-scene':scene,
           'embedded-guard':(ROOT/'flywheel-review/foldback-run.json').read_bytes()}
    prelude="const unbase64=id=>Uint8Array.from(atob(document.getElementById(id).textContent.trim()),c=>c.charCodeAt(0));\n"
    js=prelude+js
    js=replace_required(js,"fetch('observatory.json')", "Promise.resolve(new Response(unbase64('embedded-data')))")
    js=replace_required(js,"fetch('../flywheel-review/foldback-run.json')", "Promise.resolve(new Response(unbase64('embedded-guard')))" )
    js=replace_required(js,"fetch('../flywheel-review/atlas/out/atlas.json')", "Promise.resolve(new Response(unbase64('embedded-atlas')))")
    js=replace_required(js,"await browser.loadURL(new X3D.MFString('observatory.x3d'));", "await browser.replaceWorld(await browser.createX3DFromString(new TextDecoder().decode(unbase64('embedded-scene'))));")
    js=replace_required(js,"sceneControls.forEach(id=>$(id).disabled=false)", "sceneControls.filter(id=>id!=='#labels').forEach(id=>$(id).disabled=false)")
    js=replace_required(js,"const score=$('#score');", "const score=$('#score');$('#sound').disabled=true;$('#sound').title='The original score is included in the full project ZIP.';")
    html=replace_required(html,'<link rel="stylesheet" href="../vendor/x_ite/x_ite.css">','')
    html=replace_required(html,'<link rel="stylesheet" href="observatory.css">','<style>'+css+'</style>')
    html=replace_required(html,'<script src="../vendor/x_ite/x_ite.min.js"></script>','<script>'+safe_script(text_component)+'</script>\n<script>'+safe_script(engine)+'</script>')
    html=replace_required(html,'<script type="module" src="observatory.js"></script>','')
    html=replace_required(html,'href="../flywheel-review/ATLAS-INSIGHTS.html"','href="X3D-Flywheel-Atlas.html"')
    html=replace_required(html,'href="../evidence-lab/"','href="evidence-lab/"')
    html=replace_required(html,'<a href="cinematic.html">Original cinematic ↗</a>','<span>Single file · full score and 3D labels in source ZIP</span>')
    html=replace_required(html,'<audio id="score" src="loop.wav" loop preload="none"></audio>','<audio id="score"></audio>')
    html=replace_required(html,'id="labels" aria-pressed="true">Labels','id="labels" title="Labels are in the domain dock in this edition" aria-pressed="true">Dock labels')
    html=replace_required(html,'</footer>', '</footer><details style="padding:16px 34px;color:#8292ab;font-size:10px"><summary>Third party notices</summary><pre style="white-space:pre-wrap">'+__import__('html').escape((ROOT/'vendor/x_ite/LICENSE.md').read_text()+'\n\nPT Sans (embedded for X_ITE labels):\n'+(ROOT/'vendor/x_ite/assets/fonts/PT_Sans/OFL.txt').read_text())+'</pre></details>')
    payload='\n'.join('<script type="application/octet-stream" id="'+k+'">'+encoded(v)+'</script>' for k,v in blobs.items())
    html=replace_required(html,'</body>',payload+'\n<script type="module">'+safe_script(js)+'</script></body>')
    output.write_text(html,encoding='utf-8')
    print(output.name,output.stat().st_size,'bytes')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'Gobbler-Evidence-Loom.html')
    args=parser.parse_args()
    build(args.output)
