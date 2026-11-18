#!/usr/bin/env python3
"""Render an authored studio still from the actual intervention X3D import.

Blender --background --factory-startup --threads 2 --python-exit-code 1
--python tools/render_intervention.py -- --addon-root /path/to/x3d-blender-io
No native X_ITE, shader execution, interaction or color-parity claim is made.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'evidence-lab/instruments.x3d')
    parser.add_argument('--addon-root',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/assets/intervention-preview.png')
    parser.add_argument('--receipt',type=Path,default=ROOT/'receipts/review-blender.json')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    import bpy
    from mathutils import Vector

    raw=args.input.read_bytes();xml=ET.fromstring(raw)
    names={n.get('DEF'):n for n in xml.iter() if n.get('DEF')}
    parent={c:p for p in xml.iter() for c in p}
    expected={}
    for i in range(3):
        mechanism=names[f'Mechanism{i}'];position=parent[mechanism].get('translation')
        xyz=tuple(float(x) for x in position.split())
        expected[i]={'source_x3d_center':xyz,'blender_center':(xyz[0],-xyz[2],xyz[1]),
            'ring_source_vertices':len(mechanism.find('.//Coordinate').get('point').split())//3}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with tempfile.TemporaryDirectory(prefix='gobbler-intervention-import-') as temp:
        package=Path(temp)/'io_scene_x3d';package.symlink_to(args.addon_root.resolve()/'source',target_is_directory=True)
        sys.path.insert(0,temp);addon=importlib.import_module('io_scene_x3d');addon.register()
        bpy.ops.import_scene.x3d(filepath=str(args.input.resolve()),axis_forward='-Z',axis_up='Y',circle_divisions=32,color_space='SRGB',light_units='BLENDER')
        imported=list(bpy.data.objects)
        def bounds_center(objects):
            points=[ob.matrix_world@v.co for ob in objects for v in ob.data.vertices]
            if not points:raise RuntimeError('Required imported geometry is absent')
            return [(min(p[k] for p in points)+max(p[k] for p in points))/2 for k in range(3)]
        comparisons=[]
        for i,target in expected.items():
            gate=[ob for ob in imported if ob.type=='MESH' and any(mat and mat.name.split('.')[0]==f'Gate{i}' for mat in ob.data.materials)]
            if len(gate)!=1:raise RuntimeError(f'Expected one actual imported Gate{i} box, found {len(gate)}')
            members=[ob for ob in imported if ob.type=='MESH' and f'Mechanism{i}' in str(ob.get('x3d_def_path','')).split('/')]
            ring=[ob for ob in members if len(ob.data.vertices)==target['ring_source_vertices']]
            if len(ring)!=1:raise RuntimeError(f'Expected one actual imported Mechanism{i} torus, found {len(ring)}')
            gate_center=bounds_center(gate);ring_center=bounds_center(ring)
            error=max(abs(a-b) for actual in (gate_center,ring_center) for a,b in zip(actual,target['blender_center']))
            if error>2e-5:raise RuntimeError(f'Imported mechanism center differs: {i}/{error}')
            comparisons.append({'index':i,**target,'gate_mesh_parts':len(gate),'mechanism_mesh_parts':len(members),
                'ring_mesh_parts':len(ring),'ring_imported_vertices':len(ring[0].data.vertices),
                'gate_actual_bbox_center':gate_center,'ring_actual_bbox_center':ring_center,'max_absolute_error':error})
        science=bpy.data.collections.new('Actual_Imported_X3D');bpy.context.scene.collection.children.link(science)
        studio=bpy.data.collections.new('Authored_Studio');bpy.context.scene.collection.children.link(studio)
        hidden_text=[];curves=0
        for ob in imported:
            for c in list(ob.users_collection):c.objects.unlink(ob)
            science.objects.link(ob)
            if ob.type in ('LIGHT','CAMERA'):ob.hide_render=True
            if ob.type=='FONT':ob.hide_render=True;hidden_text.append(ob.name)
            if ob.type=='CURVE':ob.data.bevel_depth=.018;ob.data.bevel_resolution=2;curves+=1
        for mat in bpy.data.materials:
            if mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type=='BSDF_PRINCIPLED':
                        node.inputs['Roughness'].default_value=.27
                        node.inputs['Metallic'].default_value=.46
        def area(name,position,power,color,size):
            data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
            ob=bpy.data.objects.new(name,data);studio.objects.link(ob);ob.location=position
            ob.rotation_euler=(Vector((0,0,0))-ob.location).to_track_quat('-Z','Y').to_euler()
        area('Cool_Key',(-8,-10,12),3600,(.44,.77,1),12)
        area('Warm_Fill',(8,-4,10),2900,(1,.76,.45),10)
        area('Mint_Rim',(0,6,9),4800,(.51,1,.82),12)
        floor_material=bpy.data.materials.new('Studio_Midnight');floor_material.use_nodes=True
        bsdf=floor_material.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.008,.02,.027,1);bsdf.inputs['Metallic'].default_value=.26;bsdf.inputs['Roughness'].default_value=.34
        bpy.ops.mesh.primitive_plane_add(size=180,location=(0,0,-3.34));floor=bpy.context.object;floor.name='Studio_Floor'
        for c in list(floor.users_collection):c.objects.unlink(floor)
        studio.objects.link(floor);floor.data.materials.append(floor_material)
        camera_data=bpy.data.cameras.new('Studio_Camera');camera=bpy.data.objects.new('Studio_Camera',camera_data);studio.objects.link(camera)
        camera.location=(13,-34,12);target=Vector((0,0,-.2));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=30
        # Re-author the same three source labels with Blender's bundled font:
        # this is presentation typography, not an importer fidelity claim.
        label_material=bpy.data.materials.new('Studio_Label');label_material.diffuse_color=(.72,.86,.83,1);label_material.use_nodes=True
        bsdf=label_material.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.72,.86,.83,1);bsdf.inputs['Emission Color'].default_value=(.12,.25,.24,1)
        source_labels=[json.loads(n.get('string')) for n in xml.iter('Text')]
        for i,label in enumerate(source_labels):
            data=bpy.data.curves.new('Studio_Label','FONT');data.body=label;data.align_x='CENTER';data.size=.30;data.extrude=.002
            ob=bpy.data.objects.new('Studio_'+label,data);studio.objects.link(ob);ob.location=(expected[i]['blender_center'][0],-3.6,-2.85);ob.rotation_euler=camera.rotation_euler;data.materials.append(label_material)
        scene=bpy.context.scene;scene.camera=camera
        scene.world=bpy.data.worlds.new('Studio_World');scene.world.use_nodes=True
        scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.015,.035,.055,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3
        scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.cycles.seed=1802
        scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
        scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
        args.output.parent.mkdir(parents=True,exist_ok=True);args.receipt.parent.mkdir(parents=True,exist_ok=True)
        scene.render.filepath=str(args.output.resolve());scene.render.image_settings.file_format='PNG'
        start=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
        if sha(args.input)!=hashlib.sha256(raw).hexdigest():raise RuntimeError('Source changed during the render')
        report={'schema':'gobbler.intervention-blender-preview/1','status':'pass','created_utc':datetime.now(timezone.utc).isoformat(),
            'source':args.input.resolve().relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(raw).hexdigest(),
            'tool_sha256':sha(__file__),'blender_version':bpy.app.version_string,'blender_build':bpy.app.build_hash.decode(),'binary_sha256':sha(bpy.app.binary_path),
            'importer_repository':'https://github.com/hagopjay/x3d-blender-io','importer_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=args.addon_root,text=True).strip(),
            'import_source_sha256':{name:sha(args.addon_root/'source'/name) for name in ('__init__.py','import_x3d.py')},
            'imported_objects':len(imported),'occupancy':{'status':'pass','mechanisms':3,'gates':3,'rings':3,'comparisons':comparisons,'tolerance':2e-5,
                'axis_projection':'X3D Y-up / -Z-forward -> Blender (x,-z,y).','scope':'Actual imported mesh bounding-box centers and ring vertex counts. Not topology/material/interaction equivalence.'},
            'presentation_projection':{'hidden_imported_text_objects':hidden_text,'studio_labels':source_labels,'imported_curves_given_bevel':curves},
            'render':{'engine':'Cycles','device':'CPU','threads':2,'samples':32,'width':1280,'height':720,'seed':1802,'elapsed_seconds':elapsed,'view_transform':scene.view_settings.view_transform,'look':scene.view_settings.look},
            'image_sha256':sha(args.output),'image_bytes':args.output.stat().st_size,
            'appearance_changes':['Imported lights/camera disabled; studio camera and three area lights authored.','Imported Principled roughness/metallic adjusted for a studio still.','Imported Text hidden and the same three labels re-authored using Blender bundled font.','Separate studio floor; any imported zero-width curves receive a thin bevel.'],
            'scope':'Authored offline Blender studio still from actual portable X3D import. Not native X_ITE pixels, browser interaction, evidence-gate execution, color parity or GPU timing.'}
        args.receipt.write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'status':'pass','mechanisms':3,'image':str(args.output),'elapsed_seconds':elapsed}))


if __name__=='__main__':main()
