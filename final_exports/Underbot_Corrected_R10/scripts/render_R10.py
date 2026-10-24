"""Render the exported R10 geometry; preview or final review views."""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
from mathutils import Vector

p=argparse.ArgumentParser()
p.add_argument('--output',type=Path,required=True)
p.add_argument('--preview',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=a.output.resolve()
scene=bpy.context.scene;cam=scene.camera
objects=[o for o in bpy.data.objects if o.get('source_part_name')]
manifest=json.loads((out/'geometry_export_manifest.json').read_text())
source=json.loads((out/'underbot_description/config/geometry_manifest.json').read_text())
base_names=[]
for part in source['links']['base_link']['parts']:
    if part['name']=='chassis_adapter':break
    base_names.append(part['name'])
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='CUDA';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='CUDA'
    if any(d.type=='CUDA' for d in prefs.devices):scene.cycles.device='GPU'
except Exception as e:print('CPU fallback',str(e))
scene.cycles.samples=16 if a.preview else 48
scene.cycles.use_denoising=True
views=[('hero',(1.40,-1.55,1.10),(-.07,0,.385),1.14,False,False),
       ('base',(1.10,-1.3,.85),(0,0,.10),.72,False,True)] if a.preview else [
       ('hero',(1.40,-1.55,1.10),(-.07,0,.385),1.14,False,False),
       ('rear',(-1.35,1.40,.98),(-.07,0,.385),1.14,False,False),
       ('cutaway',(1.25,-1.45,1.08),(-.07,0,.385),1.14,True,False),
       ('base',(1.10,-1.3,.85),(0,0,.10),.72,False,True),
       ('base_top',(0,0,2.0),(0,0,0),.66,False,True)]
results=[]
for name,pos,target,scale,cut,base_only in views:
    hidden=[]
    for obj in objects:
        pn=obj['source_part_name'];link=obj.get('source_link','')
        hide=(cut and (pn.startswith(('front_door_','side_-1_','panel_screw_-1_','front_hinge_')) or pn=='front_latch'))
        if base_only:
            hide=not ((link=='base_link' and pn in base_names) or link in ('left_wheel','right_wheel','caster_link','caster_swivel_link'))
        obj.hide_render=hide
        if hide:hidden.append(obj.name)
    cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
    scene.render.resolution_x=1600 if base_only else 2200
    scene.render.resolution_y=(1600 if name=='base_top' else 1100) if base_only else 2400
    scene.render.resolution_percentage=45 if a.preview else 100
    path=out/'renders'/('Underbot_R10_'+name+('_preview' if a.preview else '')+'.png')
    scene.render.filepath=str(path)
    print('RENDER',path.name,flush=True);bpy.ops.render.render(write_still=True)
    results.append({'path':path.relative_to(out).as_posix(),'size_px':[scene.render.resolution_x,scene.render.resolution_y],
                    'removed_for_cutaway_or_base_view':hidden,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
for obj in objects:obj.hide_render=False
if not a.preview:
    report=json.loads((out/'build_report.json').read_text())
    report['renders']=results
    report['saved_scene']='models/Underbot_R10_studio.blend'
    (out/'build_report.json').write_text(json.dumps(report,indent=2)+'\n')
print('R10_RENDER_COMPLETE',len(results),flush=True)
