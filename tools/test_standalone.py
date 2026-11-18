"""Export contract controls, including actual rewritten JavaScript syntax."""
from importlib.util import module_from_spec, spec_from_file_location
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import base64

ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location('gobbler_standalone',ROOT/'gobbler-flyte/build_standalone.py')
module=module_from_spec(spec);spec.loader.exec_module(module)


class Scripts(HTMLParser):
    def __init__(self):super().__init__();self.current=None;self.rows=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script':self.current=[dict(attrs),[]]
    def handle_data(self,data):
        if self.current:self.current[1].append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.current:self.rows.append((self.current[0],''.join(self.current[1])));self.current=None


class StandaloneTests(unittest.TestCase):
    def test_missing_and_duplicate_contracts_refuse_export(self):
        self.assertEqual(module.replace_required('before PIN after','PIN','BOUND'),'before BOUND after')
        for source in ['missing','PIN then PIN']:
            with self.assertRaisesRegex(ValueError,'expected one anchor'):
                module.replace_required(source,'PIN','BOUND')

    def test_embedded_scene_and_rewritten_program(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'single.html';module.build(target)
            parser=Scripts();parser.feed(target.read_text())
            payloads={a.get('id'):s for a,s in parser.rows if a.get('type')=='application/octet-stream'}
            self.assertEqual(set(payloads),{'embedded-data','embedded-atlas','embedded-scene','embedded-guard'})
            tree=ET.fromstring(base64.b64decode(payloads['embedded-scene']))
            self.assertFalse(list(tree.iter('Text')))
            programs=[s for a,s in parser.rows if a.get('type')=='module']
            self.assertEqual(len(programs),1)
            self.assertIn("unbase64('embedded-scene')",programs[0])
            self.assertNotIn("fetch('observatory.json')",programs[0])
            self.assertNotIn("new X3D.MFString('observatory.x3d')",programs[0])
            self.assertTrue(shutil.which('node'),'Node is required for the actual export syntax gate')
            result=subprocess.run(['node','--check','--input-type=module'],input=programs[0],text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_script_terminator_does_not_escape_embedding(self):
        escaped=module.safe_script('const text="</ScRiPt><script>";')
        self.assertNotIn('</script',escaped.lower())


if __name__=='__main__':unittest.main()
