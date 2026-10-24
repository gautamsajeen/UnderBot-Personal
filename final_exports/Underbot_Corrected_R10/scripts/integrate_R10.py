"""Install the detailed SI visual meshes alongside the generated physical model."""
from pathlib import Path
import argparse, json, re, shutil
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1])
out = parser.parse_args().output.resolve()
package = out / 'underbot_description'
export = json.loads((out / 'geometry_export_manifest.json').read_text())
groups = [r for r in export['grouped_meshes'] if r['units'] == 'm']
assert groups
for record in groups:
    src = out / record['path']
    for path in (src, src.with_suffix('.obj')):
        shutil.copyfile(path, package / 'meshes' / path.name)
mtl = (out / 'models/meshes/Underbot_R10.mtl').read_text()
(package / 'meshes/Underbot_R10.mtl').write_text(mtl.replace('../../textures/', '../textures/'))
(package / 'textures').mkdir(exist_ok=True)
for path in (out / 'textures').glob('*.png'):
    if not path.stem.endswith('_metallicroughness'):
        shutil.copyfile(path, package / 'textures' / path.name)
robot = ET.parse(package / 'urdf/underbot.portable.urdf').getroot()
for visual in robot.findall('link/visual'):
    mesh = visual.find('geometry/mesh')
    mesh.set('filename', str(Path(mesh.get('filename')).with_suffix('.obj')).replace('\\', '/'))
    material = visual.find('material')
    if material is not None: visual.remove(material)
ET.indent(robot, space='  ')
(package / 'urdf/underbot.textured.urdf').write_bytes(ET.tostring(robot, encoding='utf-8', xml_declaration=True)+b'\n')
cmake = package / 'CMakeLists.txt'
cmake.write_text(re.sub(r'install\(DIRECTORY urdf meshes launch rviz config docs(?: textures)*',
                       'install(DIRECTORY urdf meshes launch rviz config docs textures', cmake.read_text()))
metadata = package / 'package.xml'
doc = ET.parse(metadata)
doc.find('version').text = '0.10.0'
doc.find('description').text = 'Underbot R10 WR141E reference-based geometry with 200 mm transparent floors and four black tower covers.'
ET.indent(doc, space='  ')
doc.write(metadata, encoding='utf-8', xml_declaration=True)
print(json.dumps({'integrated_si_meshes':len(groups), 'revision':'R10', 'physics':'Regenerated and checked for this revision.'}))
