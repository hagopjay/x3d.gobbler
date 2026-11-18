#!/usr/bin/env python3
"""Independent geometric controls for the actual scene writers; no pixel claim."""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'gobbler-flyte'
spec = importlib.util.spec_from_file_location('gobbler_scene_writer', DEMO / 'build_observatory.py')
writer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writer)


def vec(text):
    return tuple(float(x) for x in text.split())


def normalized(vector):
    length = math.hypot(*vector)
    if not length:
        raise ValueError('A geometric axis cannot be zero')
    return tuple(x / length for x in vector)


def rotate(vector, axis_angle):
    """Independent Rodrigues action; not the writer's matrix/quaternion route."""
    angle = axis_angle[3]
    if abs(angle) < 1e-12:
        return tuple(vector)
    a = normalized(axis_angle[:3])
    cosine, sine = math.cos(angle), math.sin(angle)
    dot = sum(a[i]*vector[i] for i in range(3))
    cross = (a[1]*vector[2]-a[2]*vector[1], a[2]*vector[0]-a[0]*vector[2], a[0]*vector[1]-a[1]*vector[0])
    return tuple(vector[i]*cosine + cross[i]*sine + a[i]*dot*(1-cosine) for i in range(3))


def source_parts(tree):
    result = []
    for part in tree.iter('ShaderPart'):
        literal = part.get('url')
        if literal is None:
            raise ValueError('Shader source must have an explicit URL channel')
        uri = json.loads(literal)
        if not uri.startswith('data:x-shader/') or ',' not in uri:
            raise ValueError('Expected one explicit shader data URI')
        result.append(unquote(uri.split(',', 1)[1]))
    return result


class SceneGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory(prefix='gobbler-geometric-controls-')
        target = Path(cls.folder.name)
        for name in ('build.py', 'build_observatory.py', 'observatory.json'):
            shutil.copy2(DEMO / name, target / name)
        # Build both actual writers in isolation: committed outputs cannot mask
        # a generator defect and this test does not mutate release artifacts.
        for script in ('build.py', 'build_observatory.py'):
            subprocess.run([sys.executable, str(target / script)], check=True, capture_output=True)
        cls.target = target
        cls.observatory = ET.parse(target / 'observatory.x3d')
        cls.cinematic = ET.parse(target / 'scene.x3d')

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def assertVectorAlmostEqual(self, actual, expected, tolerance=1e-10):
        self.assertEqual(len(actual), len(expected))
        for a, b in zip(actual, expected):
            self.assertAlmostEqual(a, b, delta=tolerance)

    def test_camera_known_directions_poles_and_half_turn(self):
        for target in ((0,0,-1), (0,0,1), (1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (2,3,4), (1e-8,1,1e-8)):
            with self.subTest(target=target):
                orientation = writer.look_at((0,0,0), target)
                self.assertTrue(all(math.isfinite(x) for x in orientation))
                self.assertVectorAlmostEqual(rotate((0,0,-1), orientation), normalized(target))
                if orientation[3]:
                    self.assertAlmostEqual(math.hypot(*orientation[:3]), 1.)
        with self.assertRaises(ValueError):
            rotate((0,0,-1), (0,0,0,math.pi))  # paired zero-axis mutant

    def test_camera_rejects_undefined_input(self):
        for eye, target in (((0,0,0),(0,0,0)), ((math.nan,0,0),(0,0,1)), ((0,0,0),(math.inf,0,0)), ((0,0),(1,2,3))):
            with self.subTest(eye=eye, target=target), self.assertRaises(ValueError):
                writer.look_at(eye, target)

    def test_written_viewpoints_aim_at_their_declared_centers(self):
        # Cinematic V_tour/V_front intentionally use a separately animated or
        # authored aim rather than their navigation pivot; test actual targets.
        for scene in (self.observatory, self.cinematic):
            for viewpoint in scene.iter('Viewpoint'):
                name = viewpoint.get('DEF')
                if name in ('V_tour', 'V_front', 'V_above'):
                    continue
                eye, center = vec(viewpoint.get('position')), vec(viewpoint.get('centerOfRotation'))
                expected = normalized(tuple(center[i]-eye[i] for i in range(3)))
                actual = rotate((0,0,-1), vec(viewpoint.get('orientation', '0 1 0 0')))
                with self.subTest(view=name):
                    self.assertVectorAlmostEqual(actual, expected, tolerance=.002)

    def test_feather_tethers_start_at_actual_world_eye_centers(self):
        nodes = {n.get('DEF'): n for n in self.observatory.iter() if n.get('DEF')}
        manifest = json.loads((DEMO / 'observatory.json').read_text())
        for i in range(len(manifest['domains'])):
            frame, eye, flow = (nodes[p+str(i)] for p in ('FeatherFrame','Eye','Flow'))
            local = vec(eye.get('translation'))
            position = rotate(local, vec(frame.get('rotation')))
            offset = vec(frame.get('translation'))
            actual = tuple(position[k]+offset[k] for k in range(3))
            path_start = vec(flow.get('keyValue'))[:3]
            with self.subTest(feather=i):
                self.assertVectorAlmostEqual(path_start, actual, tolerance=5.1e-5)

    def test_torus_topology_bounds_and_outward_winding(self):
        writer.MESHES.clear()
        torus = ET.fromstring(writer.torus(2., .2, 12, 8))
        points = vec(torus.find('Coordinate').get('point'))
        triples = [points[i:i+3] for i in range(0,len(points),3)]
        self.assertEqual(len(triples), 12*8)
        indices = [int(x) for x in torus.get('coordIndex').split()]
        faces = [indices[i:i+4] for i in range(0,len(indices),5)]
        self.assertEqual(len(faces), 12*8)
        self.assertEqual(indices[4::5], [-1]*(12*8))
        self.assertTrue(all(0 <= i < len(triples) for face in faces for i in face))
        for p in triples:
            self.assertAlmostEqual((math.hypot(p[0],p[1])-2.)**2+p[2]**2, .2**2, delta=4e-5)
        a,b,c=(triples[index] for index in faces[0][:3])
        u=tuple(b[i]-a[i] for i in range(3)); w=tuple(c[i]-a[i] for i in range(3))
        normal=(u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0])
        self.assertGreater(normal[0],0, 'outermost torus face must point outward')
        use = ET.fromstring(writer.torus(2., .2, 12, 8))
        self.assertEqual(use.get('USE'), torus.get('DEF'))
        self.assertEqual(len(use), 0)

    def test_vanes_use_explicit_nonzero_triangles(self):
        vanes=[n for n in self.observatory.iter('IndexedFaceSet') if n.get('DEF','').startswith('VaneMesh')]
        self.assertEqual(len(vanes),12)
        for mesh in vanes:
            flat=vec(mesh.find('Coordinate').get('point'))
            points=[flat[i:i+3] for i in range(0,len(flat),3)]
            indices=[int(x) for x in mesh.get('coordIndex').split()]
            self.assertEqual(indices[3::4],[-1]*(44*4))
            self.assertEqual(len(indices),44*4*4)
            for offset in range(0,len(indices),4):
                a,b,c=(points[i] for i in indices[offset:offset+3])
                u=tuple(b[i]-a[i] for i in range(3)); w=tuple(c[i]-a[i] for i in range(3))
                cross=(u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0])
                self.assertGreater(math.hypot(*cross),1e-8)

    def test_torus_rejects_degenerate_parameters(self):
        for args in ((1,0,8,6),(1,2,8,6),(1,.1,2,6),(1,.1,8,2),(1,.1,3.5,6),(math.inf,.1,8,6)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                writer.torus(*args)

    def test_label_escapes_mfstring_and_xml_layers(self):
        label='Research "A & B" / C:\\data\\new <test>'
        text=ET.fromstring(writer.text(label,(0,0,0),.4,(1,1,1))).find('.//Text')
        self.assertEqual(json.loads(text.get('string')),label)

    def test_shader_urls_roundtrip_and_literal_smoothstep_edges_ascend(self):
        shaders=source_parts(self.cinematic)
        self.assertEqual(len(shaders),4)
        self.assertTrue(all(s.startswith('#version 300 es\n') and 'void main()' in s for s in shaders))
        number=r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)'
        edges=[(float(a),float(b)) for s in shaders for a,b in re.findall(r'\bsmoothstep\(\s*('+number+r')\s*,\s*('+number+r')\s*,',s)]
        self.assertGreaterEqual(len(edges),10)
        self.assertTrue(all(a < b for a,b in edges),edges)
        broken=ET.ElementTree(ET.fromstring('<X3D><Scene><ShaderPart>void main(){}</ShaderPart></Scene></X3D>'))
        with self.assertRaises(ValueError):
            source_parts(broken)

    def test_wheel_discs_align_with_ring_plane(self):
        parents={child:parent for parent in self.cinematic.iter() for child in parent}
        discs=[n for n in self.cinematic.iter('Cylinder') if n.get('radius')=='4.1']
        self.assertEqual(len(discs),9)
        for disc in discs:
            transform=parents[parents[disc]]
            self.assertEqual(transform.tag,'Transform')
            # The default cylinder's longitudinal axis is +Y. A wheel whose
            # torus lies in XY needs that axis in ±Z, not left along +Y.
            axis=rotate((0,1,0),vec(transform.get('rotation','0 1 0 0')))
            self.assertAlmostEqual(abs(axis[2]),1.,delta=1e-8)

    def test_generated_documents_have_unique_defs_and_preceding_typed_uses(self):
        for tree in (self.observatory,self.cinematic):
            definitions={}
            for node in tree.iter():
                if node.get('DEF'):
                    self.assertNotIn(node.get('DEF'),definitions)
                    definitions[node.get('DEF')]=node.tag
                if node.get('USE'):
                    self.assertEqual(definitions.get(node.get('USE')),node.tag)
            for route in tree.iter('ROUTE'):
                self.assertIn(route.get('fromNode'),definitions)
                self.assertIn(route.get('toNode'),definitions)

    def test_writers_rebuild_byte_identically(self):
        for script, output in (('build.py','scene.x3d'),('build_observatory.py','observatory.x3d')):
            before=(self.target/output).read_bytes()
            subprocess.run([sys.executable,str(self.target/script)],check=True,capture_output=True)
            self.assertEqual(before,(self.target/output).read_bytes())
            self.assertEqual(before,(DEMO/output).read_bytes())


if __name__ == '__main__':
    unittest.main(verbosity=2)
