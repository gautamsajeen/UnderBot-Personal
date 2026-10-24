"""Check final assets and reports, then archive and verify every delivered byte."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, shutil, struct, zipfile
from PIL import Image

OUT=Path(__file__).resolve().parents[1];PKG=OUT/'underbot_description'
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def included(p):return p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.blend1','.blend2')
def inventory(folder):
    return {p.relative_to(folder).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)}
            for p in sorted(folder.rglob('*')) if included(p) and p!=folder/'validation/sha256_manifest.json'}

manifest=read(OUT/'geometry_export_manifest.json');audit=read(OUT/'validation/independent_geometry.json')
assert audit['status']=='PASS' and not audit['errors']
assert audit['exports']['inventory_sha256']==digest(OUT/'geometry_export_manifest.json')
assert manifest['source_sha256']==digest(PKG/'config/geometry_manifest.json')
assert audit['textured_glb']['sha256']==digest(OUT/'models/Underbot_R10_textured.glb')
for record in manifest['components']+manifest['grouped_meshes']+[manifest['assembled']]:
    assert digest(OUT/record['path'])==record['sha256'],record['path']
for record in manifest['grouped_meshes']:
    if record['units']=='m':assert digest(PKG/'meshes'/Path(record['path']).name)==record['sha256']

core=digest(PKG/'urdf/underbot.urdf');portable=digest(PKG/'urdf/underbot.portable.urdf')
checks={}
for name,key,target in [('authoring_checks','status',core),('portable_checks','status',portable),
                        ('xacro_check','status',core),('pybullet_import_R10','status',portable),
                        ('viewer_checks_R10','status',portable),('physics_smoke','result',portable)]:
    report=read(PKG/'validation'/f'{name}.json')
    assert report[key] in ('PASS','PASS_WITH_REVIEW_NOTES'),name
    assert not report.get('errors') and report['urdf_sha256']==target,name
    checks[name]={'status':report[key],'path':f'underbot_description/validation/{name}.json',
                  'sha256':digest(PKG/'validation'/f'{name}.json')}
    if name=='pybullet_import_R10':
        for path,sha in report['mesh_sha256'].items():assert digest(PKG/path)==sha,path
    if name in ('authoring_checks','portable_checks'):
        for path,data in report['stl_meshes'].items():
            mesh=PKG/'meshes'/Path(path).name
            assert struct.unpack('<I',mesh.read_bytes()[80:84])[0]==data['triangles'],path
static=read(PKG/'validation/static_physics.json')
assert static['urdf_sha256']==core
assert static['effort_status']=='WITHIN_PROVISIONAL_LIMITS_IN_SAMPLES'
assert static['support']['arm_poses_without_positive_continuous_angle_bound']==0
checks['static_physics']={'status':'PASS_CURRENT_INPUT_HASH','path':'underbot_description/validation/static_physics.json','sha256':digest(PKG/'validation/static_physics.json')}
checks['independent_geometry']={'status':'PASS','path':'validation/independent_geometry.json','sha256':digest(OUT/'validation/independent_geometry.json')}

build=read(OUT/'build_report.json');assert len(build['renders'])==5
for record in build['renders']:
    p=OUT/record['path']
    with Image.open(p) as im:
        assert list(im.size)==record['size_px'];im.verify()
    assert digest(p)==record['sha256']
build['packed_scene_sha256']=digest(OUT/'models/Underbot_R10_studio.blend')
write(OUT/'build_report.json',build)
shutil.copyfile(OUT/'renders/Underbot_R10_hero.png',PKG/'docs/model_preview.png')

# Historical intermediate reports are retained but clearly separated from results.
history=PKG/'validation/history';history.mkdir(exist_ok=True)
for pattern in ('*initial*',):
    for p in (PKG/'validation').glob(pattern):
        if p.is_file():shutil.move(str(p),str(history/p.name))
(history/'README.md').write_text('Historical intermediate checks only. They predate the final geometry or controller and are not final results. Current reports are one directory above.\n')
for p in (PKG/'docs').glob('floor_plan_R0*.svg'):
    archive=OUT.parent/'R10_superseded_inputs';archive.mkdir(exist_ok=True)
    shutil.move(str(p),str(archive/p.name))
for p in (OUT/'models').glob('*.blend[12]'):
    archive=OUT.parent/'R10_superseded_inputs';archive.mkdir(exist_ok=True)
    shutil.move(str(p),str(archive/p.name))

summary={'revision':'R10','status':'PASS_WITH_DOCUMENTED_ESTIMATES','generated_at_utc':datetime.now(timezone.utc).isoformat(),
         'source_geometry_sha256':digest(PKG/'config/geometry_manifest.json'),'core_urdf_sha256':core,'portable_urdf_sha256':portable,
         'component_count':len(manifest['components']),'triangle_count':manifest['assembled']['triangles'],
         'independent_checks':audit['check_count'],'mass_kg':audit['final_urdf']['modeled_mass_kg'],
         'floor_frame_mm':[200,200],'covered_body_mm':[204,204],'post_mm':[20,20,500],
         'reports':checks,'review_notes':read(PKG/'validation/authoring_checks.json')['warnings'],
         'limits':audit['notes'],'native_Gazebo_Isaac_RViz_FreeCAD_tested':False}
write(OUT/'validation/final_verification.json',summary)
write(OUT/'validation/final_delivery.json',summary)
shutil.copyfile(OUT/'validation/final_verification.md',PKG/'validation/final_verification.md')
for ext in ('json','md'):shutil.copyfile(OUT/f'validation/independent_geometry.{ext}',PKG/f'validation/independent_geometry.{ext}')
package_summary=json.loads(json.dumps(summary))
for record in package_summary['reports'].values():record['path']=record['path'].removeprefix('underbot_description/')
write(PKG/'validation/final_verification.json',package_summary)

# Check local Markdown links in both deliverable READMEs.
for document in (OUT/'README.md',PKG/'README.md'):
    for target in re.findall(r'\]\(([^)]+)\)',document.read_text(encoding='utf-8')):
        if not target.startswith(('https:','http:','#')):assert (document.parent/target.split('#')[0]).exists(),target
write(PKG/'validation/sha256_manifest.json',{'files':inventory(PKG)})
write(OUT/'validation/sha256_manifest.json',{'files':inventory(OUT)})
files=inventory(OUT)
archive=OUT.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(OUT.rglob('*')):
        if included(p):z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for path,record in files.items():
        assert hashlib.sha256(z.read(OUT.name+'/'+path)).hexdigest()==record['sha256'],path
result={'status':'PASS','archive':str(archive),'bytes':archive.stat().st_size,'sha256':digest(archive),'files':len(files)+1}
write(OUT.parent/'Underbot_Corrected_R10_archive_check.json',result)
print(json.dumps(result,indent=2))
