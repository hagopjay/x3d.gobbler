"""Exercise the actual publication sweep on pending filenames and Git errors."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE=Path(__file__).with_name('leak_sweep.py')


class SweepTests(unittest.TestCase):
    def fixture(self,root):
        tools=root/'tools';tools.mkdir();target=tools/'leak_sweep.py';shutil.copyfile(SOURCE,target);return target

    def test_pending_file_with_spaces_is_scanned(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);script=self.fixture(root)
            subprocess.run(['git','init','-q',str(root)],check=True,capture_output=True)
            (root/'pending file.mjs').write_text('token = '+repr('sk-'+'a'*24))
            run=subprocess.run([sys.executable,str(script)],capture_output=True,text=True)
            self.assertEqual(run.returncode,1)
            self.assertIn('pending file.mjs: key-shaped string',run.stdout)

    def test_failed_inventory_is_not_an_empty_clean_project(self):
        with tempfile.TemporaryDirectory() as directory:
            script=self.fixture(Path(directory))
            run=subprocess.run([sys.executable,str(script)],capture_output=True,text=True)
            self.assertEqual(run.returncode,1)
            self.assertIn('could not enumerate',run.stderr)


if __name__=='__main__':unittest.main()
