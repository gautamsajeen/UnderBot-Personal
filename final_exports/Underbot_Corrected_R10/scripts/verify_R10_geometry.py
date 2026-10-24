"""Independent final-export dimensional checks; never imports the build generator.

Uses source design records for component names, but hard-coded accepted user
dimensions for the floor/frame/cover checks. All dimensions are normalized to SI.
This is a digital-geometry audit, not a real-hardware measurement/certification.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from io import BytesIO
import itertools
import json
import math
from pathlib import Path
import struct
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rot(rpy):
    roll, pitch, yaw = rpy
    cx, sx = math.cos(roll), math.sin(roll)
    cy, sy = math.cos(pitch), math.sin(pitch)
    cz, sz = math.cos(yaw), math.sin(yaw)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return rz @ ry @ rx


def vec(text, default=(0., 0., 0.)):
    return np.asarray([float(x) for x in text.split()] if text else default)


def transform(element):
    result = np.eye(4)
    if element is not None:
        result[:3, :3] = rot(vec(element.get('rpy')))
        result[:3, 3] = vec(element.get('xyz'))
    return result


def part_bounds(part):
    kind, size = part['kind'], part['size']
    if kind == 'loft':
        points = np.asarray(part['vertices'], dtype=float)
    elif kind == 'prism':
        points = np.array([[*xy, z] for xy in part['polygon'] for z in (-size[2]/2, size[2]/2)])
    elif kind == 'extrusion':
        points = np.array(list(itertools.product((-.010, .010), (-.010, .010), (-size[0]/2, size[0]/2))))
    elif kind == 'box':
        points = np.array(list(itertools.product(*[(-s/2, s/2) for s in size])))
    elif kind == 'cylinder':
        radius, length = size
        rotation = rot(part['rpy'])
        half = np.sqrt(rotation[:, 0]**2 + rotation[:, 1]**2)*radius + np.abs(rotation[:, 2])*length/2
        return np.array(part['xyz'])-half, np.array(part['xyz'])+half
    else:
        radius = size[0]
        return np.array(part['xyz'])-radius, np.array(part['xyz'])+radius
    points = points @ rot(part['rpy']).T + np.asarray(part['xyz'])
    return points.min(0), points.max(0)


def combined_bounds(parts):
    bounds = [part_bounds(p) for p in parts]
    return np.min([b[0] for b in bounds], axis=0), np.max([b[1] for b in bounds], axis=0)


def stl_read(path):
    data = Path(path).read_bytes()
    if len(data) >= 84 and len(data) == 84 + struct.unpack_from('<I', data, 80)[0]*50:
        count = struct.unpack_from('<I', data, 80)[0]
        dtype = np.dtype([('normal', '<f4', 3), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])
        parsed = np.frombuffer(data, dtype=dtype, count=count, offset=84)
        return parsed['vertices'].astype(float), parsed['normal'].astype(float)
    points, normals = [], []
    for line in data.decode('ascii').splitlines():
        pieces = line.strip().split()
        if pieces and pieces[0] == 'vertex':
            points.append(list(map(float, pieces[1:4])))
        elif pieces[:2] == ['facet', 'normal']:
            normals.append(list(map(float, pieces[2:5])))
    return np.asarray(points).reshape(-1, 3, 3), np.asarray(normals)


def stl_stats(path, scale=1.):
    triangles, normals = stl_read(path)
    triangles *= scale
    if not len(triangles) or not np.isfinite(triangles).all():
        raise ValueError('Empty or non-finite mesh')
    cross = np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0])
    double_area = np.linalg.norm(cross, axis=1)
    bad = double_area < 1e-18
    normal_dots = np.einsum('ij,ij->i', cross, normals)
    # Quantize after SI normalization: equivalent mm/m exports have equal topology.
    vertices = np.round(triangles.reshape(-1, 3)/1e-9).astype(np.int64)
    unique, inverse = np.unique(vertices, axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    raw_edges = np.concatenate((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))
    directed = np.where(raw_edges[:, 0] < raw_edges[:, 1], 1, -1)
    edges = np.sort(raw_edges, axis=1)
    _, inverse_edge, counts = np.unique(edges, axis=0, return_counts=True, return_inverse=True)
    orientation = np.bincount(inverse_edge, weights=directed)
    volume = np.einsum('ij,ij->i', triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])).sum()/6
    return {
        'sha256': digest(path), 'triangles': len(triangles), 'unique_vertices_1nm': len(unique),
        'bounds_min_m': triangles.min((0, 1)).tolist(), 'bounds_max_m': triangles.max((0, 1)).tolist(),
        'dimensions_m': np.ptp(triangles.reshape(-1, 3), axis=0).tolist(),
        'degenerate_triangles': int(bad.sum()), 'boundary_edges': int((counts == 1).sum()),
        'nonmanifold_edges': int((counts > 2).sum()),
        'unbalanced_oriented_edges': int((orientation != 0).sum()),
        'nonpositive_normal_alignment': int((normal_dots[~bad] <= 0).sum()),
        'signed_shell_volume_m3': float(volume),
        'closed_oriented_shells': bool(np.all(counts >= 2) and np.all(counts % 2 == 0) and np.all(orientation == 0)),
        'single_manifold_edge_multiplicity': bool(np.all(counts == 2) and np.all(orientation == 0)),
    }, triangles


class Audit:
    def __init__(self):
        self.checks, self.errors, self.notes = [], [], []

    def check(self, name, result, measured=None, required=None):
        self.checks.append({'name': name, 'pass': bool(result), 'measured': measured, 'required': required})
        if not result:
            self.errors.append(name)

    def near(self, name, measured, expected, atol=1e-8):
        measured, expected = np.asarray(measured), np.asarray(expected)
        same = measured.shape == expected.shape
        result = same and np.allclose(measured, expected, atol=atol, rtol=0)
        if max(measured.size, expected.size)>60:
            value={'shape':list(measured.shape),'maximum_absolute_error_m':float(np.max(np.abs(measured-expected))) if same else None}
            target={'shape':list(expected.shape),'absolute_tolerance_m':atol}
        else:
            value,target=measured.tolist(),expected.tolist()
        self.check(name,result,value,target)

    def design(self, source):
        geometry = json.loads((source/'config/geometry_manifest.json').read_text())
        parts = geometry['links']['base_link']['parts']
        lookup = {p['name']: p for p in parts}
        floors = [p for p in parts if p['name'].startswith('polycarbonate_floor_')]
        posts = [p for p in parts if p['name'].startswith('post_')]
        rails = [p for p in parts if p['name'].startswith(('rail_x_', 'rail_y_'))]
        self.check('Four floor plates', len(floors) == 4, len(floors), 4)
        self.check('Four 500mm upright posts', len(posts) == 4, len(posts), 4)
        self.check('Sixteen horizontal rails', len(rails) == 16, len(rails), 16)
        for p in floors:
            lo, hi = part_bounds(p)
            self.near(p['name']+' 200x200x3mm envelope', hi-lo, [.200, .200, .003])
            poly = np.asarray(p['polygon']); other = np.roll(poly, -1, axis=0)
            area = abs(np.sum(poly[:, 0]*other[:, 1]-other[:, 0]*poly[:, 1]))/2
            self.near(p['name']+' four20mm corner reliefs area', area, .0384)
        for p in posts:
            lo, hi = part_bounds(p)
            self.near(p['name']+'20x20x500mm', hi-lo, [.020, .020, .500])
            self.near(p['name']+'bottom/top', [lo[2], hi[2]], [.205, .705])
        for p in rails:
            self.near(p['name']+'cut length160mm', p['size'], [.160])
        lo, hi = combined_bounds(posts+rails)
        self.near('Outside frame200x200mm', hi[:2]-lo[:2], [.200, .200])
        self.near('Proposed frame centred140mm rearward', (hi[:2]+lo[:2])/2, [-.140, 0])
        # Select tower panels specifically: the mower also has side_* seam details.
        covers = [p for p in parts if p['name'].startswith(('front_door_', 'side_-1_', 'side_1_')) or p['name']=='rear_door_closed']
        lo, hi = combined_bounds(covers)
        self.near('External covers204x204mm', hi[:2]-lo[:2], [.204, .204])
        for p in covers:
            self.near(p['name']+'sheet2mm', min(p['size']), .002)
            self.check(p['name']+' opaque black plastic source material', p['material']=='matte_black', p['material'], 'matte_black')
        self.check('All four sides have flat covers',
                   any(p['name'].startswith('front_door_') for p in covers)
                   and any(p['name']=='rear_door_closed' for p in covers)
                   and all(any(p['name'].startswith('side_'+str(s)+'_') for p in covers) for s in [-1,1]))
        for p in floors:
            self.check(p['name']+' transparent polycarbonate source material', p['material']=='polycarbonate')
        self.check('Camera shelf transparent polycarbonate source material', lookup['camera_shelf']['material']=='polycarbonate')
        for p in posts+rails:
            self.check(p['name']+' black aluminium profile source material', p['material']=='matte_black' and p['kind']=='extrusion')
        self.near('Proposed floor top elevations', sorted(part_bounds(p)[1][2] for p in floors), [.228,.503,.578,.708])
        self.near('Published WR141E outer envelope recorded in source', [geometry['parameters'][k] for k in ('base_length','base_width','base_height')], [.558,.404,.205])
        self.near('Supplier-confirmed rear tyre diameter', geometry['parameters']['wheel_radius']*2, .205)
        self.near('Supplier-confirmed front tyre diameter', geometry['parameters']['caster_radius']*2, .079)
        hood=lookup['wr141e_orange_hood']
        self.check('WR141E hood has shaped loft instead of constant-height prism',hood['kind']=='loft')
        if hood['kind']=='loft':
            self.check('WR141E loft has multiple height sections', len(np.unique(np.round(np.asarray(hood['vertices'])[:,2],6)))>3)
        self.check('Height dial is on robot right (-Y)',lookup['height_adjustment_dial']['xyz'][1]<0)
        self.check('STOP and display are on robot left (+Y)',lookup['stop_button']['xyz'][1]>0 and lookup['display']['xyz'][1]>0)
        contacts=[p for p in parts if 'charging_contact' in p['name']]
        self.check('Charging contacts on robot right (-Y)',len(contacts)>=3 and all(p['xyz'][1]<0 for p in contacts))
        self.stock_base_parts=[]
        for p in parts:
            if p['name']=='chassis_adapter':break
            self.stock_base_parts.append(p['name'])
        self.check('Stock chassis selection excludes tower',bool(self.stock_base_parts) and not any(p.startswith(('post_','rail_')) for p in self.stock_base_parts))
        self.near('GB70 upright published body envelope', lookup['noco_gb70']['size'], [.069, .099, .222])
        # Require physical corner reliefs, not merely a 200mm bounding square.
        for floor in floors:
            for post in posts:
                pl, ph = part_bounds(post)
                fl, fh = part_bounds(floor)
                corners = [xy for xy in floor['polygon'] if abs(xy[0])>.099 and abs(xy[1])>.099]
                self.check(floor['name']+' excludes post '+post['name'], not corners)
        self.design_geometry = geometry
        self.notes += [
            'The floor/frame dimensions and accepted 204 mm covered body are user requirements. The 3 mm floors and 2 mm covers are proposed material thicknesses.',
            'WR141E 558 × 404 × 205 mm and upright GB70 body 69 × 99 × 222 mm are published envelopes. Replacement-part suppliers publish the 205 mm rear and 79 mm front wheel diameters; detailed chassis and battery contours remain reference-derived approximations.',
            'Rear tyre width 40 mm, track 334 mm, axle positions −170/+170 mm, caster trail 20 mm and approximate 55 mm caster width are online-reference estimates, not a factory dimensioned drawing.',
            'Bare Kinect layout, arm pivots/lengths, electronics, installed hardware masses, joint limits and motor ratings remain unmeasured design inputs. Mathematical mass/inertia checks do not certify actual hardware dynamics.',
            'The 140 mm rearward tower offset is a proposed mounting position intended to leave the controls accessible. Base attachment holes and structural load capacity are not measured or certified.',
            'Closed STL shells may overlap at fasteners/assembly interfaces. A watertight collection of shells is not a Boolean-unioned print-ready solid.',
        ]

    def urdf(self, path):
        robot = ET.parse(path).getroot()
        links = {n.get('name'): n for n in robot.findall('link')}
        joints = {n.get('name'): n for n in robot.findall('joint')}
        self.check('URDF unique link and joint names',len(links)==len(robot.findall('link')) and len(joints)==len(robot.findall('joint')))
        self.check(path.name+'23links/22joints', len(links)==23 and len(joints)==22, [len(links), len(joints)], [23, 22])
        kinds = Counter(j.get('type') for j in joints.values())
        self.check(path.name+'joint types', kinds=={'fixed':4, 'continuous':4, 'revolute':14}, dict(kinds), {'fixed':4, 'continuous':4, 'revolute':14})
        roots = set(links)-{j.find('child').get('link') for j in joints.values()}
        self.check(path.name+'one base_link root', roots=={'base_link'}, sorted(roots), ['base_link'])
        fk = {'base_link':np.eye(4)}
        pending = dict(joints)
        while pending:
            advanced = False
            for name, joint in list(pending.items()):
                parent = joint.find('parent').get('link'); child = joint.find('child').get('link')
                if parent not in fk:
                    continue
                fk[child] = fk[parent] @ transform(joint.find('origin'))
                self.near(name+'orthonormal rotation', fk[child][:3,:3].T@fk[child][:3,:3], np.eye(3))
                self.near(name+'proper rotation', np.linalg.det(fk[child][:3,:3]), 1.)
                if joint.get('type')!='fixed':
                    self.near(name+'unit axis', np.linalg.norm(vec(joint.find('axis').get('xyz'))), 1.)
                    lim=joint.find('limit')
                    self.check(name+' finite positive effort and velocity',lim is not None and all(math.isfinite(float(lim.get(k,'nan'))) and float(lim.get(k,'0'))>0 for k in ('effort','velocity')))
                    if joint.get('type')=='revolute':
                        self.check(name+' finite ordered limits including zero',lim is not None and math.isfinite(float(lim.get('lower','nan'))) and math.isfinite(float(lim.get('upper','nan'))) and float(lim.get('lower','nan'))<=0<=float(lim.get('upper','nan')) and float(lim.get('lower','nan'))<float(lim.get('upper','nan')))
                pending.pop(name); advanced = True
            if not advanced:
                self.check(path.name+'acyclic reachable tree', False); break
        for side, sign in [('left',1), ('right',-1)]:
            self.near(side+'arm mounting datum', fk[side+'_arm_base'][:3, 3], [-.140, sign*.108, .545])
            arm_names = [name for name in joints if name.startswith(side+'_') and any(t in name for t in ['arm_base_joint','shoulder_joint','elbow_joint','wrist_pitch_joint','wrist_roll_joint'])]
            self.check(side+'five positioning axes', len(arm_names)==5, len(arm_names), 5)
            leader, follower = joints[side+'_gripper_left_joint'], joints[side+'_gripper_right_joint']
            mimic = follower.find('mimic')
            self.check(side+'gripper coupling', mimic is not None and mimic.get('joint')==leader.get('name') and float(mimic.get('multiplier','1'))==1 and float(mimic.get('offset','0'))==0)
            self.near(side+'opposite jaw axes', vec(leader.find('axis').get('xyz')), -vec(follower.find('axis').get('xyz')))
            self.near(side+'forward rolling axis', vec(joints[side+'_wheel_joint'].find('axis').get('xyz')), [0,1,0])
            self.near(side+' estimated rear axle datum',fk[side+'_wheel'][:3,3],[-.170,sign*.167,.1025])
            wheel_collision=links[side+'_wheel'].find('collision/geometry/cylinder')
            self.near(side+' physical tyre radius',float(wheel_collision.get('radius')),.1025)
            self.near(side+' estimated physical tyre width',float(wheel_collision.get('length')),.040)
        self.near('Caster ground-contact datum',fk['caster_link'][:3,3],[.170,0,.0395])
        self.near('Caster spin axis',vec(joints['caster_wheel_joint'].find('axis').get('xyz')),[0,1,0])
        self.near('Caster swivel axis',vec(joints['caster_swivel_joint'].find('axis').get('xyz')),[0,0,1])
        self.near('Camera optical +Z points forward', fk['camera_optical_frame'][:3,:3] @ [0,0,1], [1,0,0])
        total_mass = 0.
        for name, link in links.items():
            inertial = link.find('inertial')
            mass = float(inertial.find('mass').get('value')); total_mass += mass
            i = inertial.find('inertia')
            tensor=np.array([[float(i.get('ixx')),float(i.get('ixy')),float(i.get('ixz'))], [float(i.get('ixy')),float(i.get('iyy')),float(i.get('iyz'))], [float(i.get('ixz')),float(i.get('iyz')),float(i.get('izz'))]])
            eig=np.linalg.eigvalsh(tensor)
            self.check(name+'physical inertia', np.all(np.isfinite(tensor)) and (mass==0 and np.all(eig==0) or mass>0 and np.all(eig>0) and eig[2] <= eig[0]+eig[1]+1e-10))
            self.check(name+' finite centre of mass',np.isfinite(transform(inertial.find('origin'))).all())
            for collision in link.findall('collision'):
                geo=collision.find('geometry')
                self.check(name+' collision has exactly one primitive',len(geo)==1)
                primitive=geo[0]
                dims=vec(primitive.get('size')) if primitive.tag=='box' else np.asarray([float(v) for k,v in primitive.attrib.items() if k in ('radius','length')])
                self.check(name+' collision finite positive geometry',primitive.tag in ('box','sphere','cylinder') and len(dims)>0 and np.isfinite(dims).all() and (dims>0).all())
            for visual in link.findall('visual'):
                mesh=visual.find('geometry/mesh')
                if mesh is None:continue
                filename=mesh.get('filename')
                asset=path.parent.parent/filename.removeprefix('package://underbot_description/') if filename.startswith('package://underbot_description/') else path.parent/filename
                self.check(name+' visual mesh resolves '+filename,asset.is_file())
                self.near(name+' visual scale is SI identity',vec(mesh.get('scale'),(1,1,1)),[1,1,1])
                self.near(name+' grouped visual frame is link-local',transform(visual.find('origin')),np.eye(4))
        self.mass = total_mass
        self.fk = fk
        return {'path':str(path), 'sha256':digest(path), 'modeled_mass_kg':total_mass}

    def exports(self, root):
        inventory_path = root/'geometry_export_manifest.json'
        inventory=json.loads(inventory_path.read_text())
        source_parts={(name,p['name']):p for name,link in self.design_geometry['links'].items() for p in link['parts']}
        exported={(r['link'],r['part']):r for r in inventory['components']}
        self.check('Every original component exported exactly once', len(exported)==len(inventory['components']) and set(exported)==set(source_parts), len(exported), len(source_parts))
        self.check('Export source manifest hash', inventory['source_sha256']==self.source_manifest_hash, inventory['source_sha256'], self.source_manifest_hash)
        metrics={}; linktri={}; worldtri=[]; world_components={}
        for key, record in exported.items():
            name=' / '.join(key); path=root/record['path']; part=source_parts[key]
            self.check(name+' millimetre part-local STL', record['units']=='mm' and record['frame']=='part_local')
            info,tri=stl_stats(path, .001)
            metrics[record['path']]=info
            self.check(name+' file hash', info['sha256']==record['sha256'])
            self.check(name+' triangle count', info['triangles']==record['triangles'],info['triangles'],record['triangles'])
            self.check(name+' no degenerate triangles', info['degenerate_triangles']==0,info['degenerate_triangles'],0)
            self.check(name+' outward STL normals',info['nonpositive_normal_alignment']==0,info['nonpositive_normal_alignment'],0)
            self.check(name+' closed consistently wound surface',info['single_manifold_edge_multiplicity'],{k:info[k] for k in ('boundary_edges','nonmanifold_edges','unbalanced_oriented_edges')})
            self.check(name+' positive signed volume',info['signed_shell_volume_m3']>0,info['signed_shell_volume_m3'])
            local_part=dict(part,xyz=[0,0,0],rpy=[0,0,0]); expected_bounds=part_bounds(local_part)
            actual_bounds=[info['bounds_min_m'],info['bounds_max_m']]
            self.near(name+' retained exact local envelope',actual_bounds,expected_bounds,2e-7)
            self.near(name+' recorded local bounds',actual_bounds,record['local_bounds_m'],2e-7)
            expected_local=np.eye(4);expected_local[:3,:3]=rot(part['rpy']);expected_local[:3,3]=part['xyz']
            self.near(name+' original part-to-link transform',record['part_to_link_m'],expected_local,2e-7)
            self.near(name+' original link-to-world transform',record['link_to_world_m'],self.fk[key[0]],2e-7)
            self.near(name+' original part-to-world transform',record['part_to_world_m'],self.fk[key[0]]@expected_local,2e-7)
            def apply(t,points):
                t=np.asarray(t)
                return points@t[:3,:3].T+t[:3,3]
            placed=apply(record['part_to_link_m'],tri)
            world=apply(record['part_to_world_m'],tri)
            linktri[key]=placed;worldtri.append(world);world_components[key]=world
            self.near(name+' recorded world bounds',[world.min((0,1)),world.max((0,1))],record['world_bounds_m'],2e-7)
        for record in inventory['grouped_meshes']:
            name=record['path']; path=root/name
            self.check(name+' explicit recognized unit',record['units'] in ('mm','m'))
            info,tri=stl_stats(path,.001 if record['units']=='mm' else 1.)
            metrics[name]=info
            self.check(name+' file hash',info['sha256']==record['sha256'])
            keys=[key for key,rec in exported.items() if key[0]==record['frame'] and ('material' not in record or rec['material_bucket']==record['material'])]
            expected=np.concatenate([linktri[k] for k in keys])
            self.check(name+' component triangle total',len(tri)==len(expected)==record['triangles'],len(tri),len(expected))
            # The manifest's ordering gives a direct vertex comparison; this is stronger
            # than a bounding-box-only check and catches mirrored/rotated/unit errors.
            self.near(name+' exact mm/metre component assembly',tri,expected,2e-7)
            self.check(name+' no degenerate triangles',info['degenerate_triangles']==0,info['degenerate_triangles'],0)
            self.check(name+' outward STL normals',info['nonpositive_normal_alignment']==0,info['nonpositive_normal_alignment'],0)
        assembled=inventory['assembled']; path=root/assembled['path']
        self.check('Assembled STL explicitly millimetres',assembled['units']=='mm')
        info,tri=stl_stats(path,.001);metrics[assembled['path']]=info
        expected=np.concatenate(worldtri)
        self.check('Assembled STL file hash',info['sha256']==assembled['sha256'])
        self.check('Assembled STL triangle total',len(tri)==len(expected)==assembled['triangles'],len(tri),len(expected))
        self.near('Assembled STL correct world transforms and mm units',tri,expected,2e-7)
        self.near('Assembled STL recorded bounds',[info['bounds_min_m'],info['bounds_max_m']],assembled['bounds_m'],2e-7)
        self.check('Assembly has no degenerate triangles',info['degenerate_triangles']==0,info['degenerate_triangles'],0)
        self.check('Assembly has outward STL normals',info['nonpositive_normal_alignment']==0,info['nonpositive_normal_alignment'],0)
        self.check('Assembly honestly identified as multiple shells',assembled['multiple_closed_shells'] and not assembled['boolean_union'])
        def selected_bounds(predicate):
            points=np.concatenate([w for key,w in world_components.items() if predicate(key)])
            return np.array([points.min((0,1)),points.max((0,1))])
        for key, points in world_components.items():
            if key[1].startswith('polycarbonate_floor_'):
                self.near('Actual STL '+key[1]+' 200x200x3mm',np.ptp(points.reshape(-1,3),axis=0),[.200,.200,.003],2e-7)
            if key[1].startswith('post_'):
                self.near('Actual STL '+key[1]+' 20x20x500mm',np.ptp(points.reshape(-1,3),axis=0),[.020,.020,.500],2e-7)
        frame=selected_bounds(lambda k:k[0]=='base_link' and k[1].startswith(('post_','rail_x_','rail_y_')))
        self.near('Actual STL outside frame200x200mm',frame[1,:2]-frame[0,:2],[.200,.200],2e-7)
        covers=selected_bounds(lambda k:k[0]=='base_link' and (k[1].startswith(('front_door_','side_-1_','side_1_')) or k[1]=='rear_door_closed'))
        self.near('Actual STL external sheets204x204mm',covers[1,:2]-covers[0,:2],[.204,.204],2e-7)
        stock=selected_bounds(lambda k:(k[0]=='base_link' and k[1] in self.stock_base_parts) or k[0] in ('left_wheel','right_wheel','caster_link','caster_swivel_link'))
        self.near('Actual stock base overall envelope558x404x205mm',stock[1]-stock[0],[.558,.404,.205],2e-7)
        self.near('Actual stock base bounds referenced to ground',stock,[[-.279,-.202,0],[.279,.202,.205]],2e-7)
        for side in ('left','right'):
            b=selected_bounds(lambda k:k[0]==side+'_wheel')
            self.near('Actual '+side+' rear wheel205mm diameter',b[1,[0,2]]-b[0,[0,2]],[.205,.205],2e-7)
        caster=selected_bounds(lambda k:k[0]=='caster_link')
        self.near('Actual front wheel79mm diameter',caster[1,[0,2]]-caster[0,[0,2]],[.079,.079],2e-7)
        self.component_world_bounds={k:np.array([v.min((0,1)),v.max((0,1))]) for k,v in world_components.items()}
        package=root/'underbot_description'
        for rec in inventory['grouped_meshes']:
            if rec['units']=='m':
                packaged=package/'meshes'/Path(rec['path']).name
                self.check('URDF package uses detailed '+packaged.name,packaged.exists() and digest(packaged)==rec['sha256'])
        return {
            'inventory_sha256':digest(inventory_path),'component_count':len(exported),
            'assembled_triangles':len(tri),'assembled_bounds_m':[info['bounds_min_m'],info['bounds_max_m']],
            'actual_frame_bounds_m':frame.tolist(),'actual_cover_bounds_m':covers.tolist(),'stock_base_bounds_m':stock.tolist(),
            'meshes':metrics,
        }

    def glb(self, root):
        path=root/'models/Underbot_R10_textured.glb';data=path.read_bytes()
        magic,version,total=struct.unpack_from('<4sII',data)
        self.check('GLB2 container length',magic==b'glTF' and version==2 and total==len(data))
        cursor=12;document=None;binary=None
        while cursor<len(data):
            length,kind=struct.unpack_from('<II',data,cursor);chunk=data[cursor+8:cursor+8+length]
            if kind==0x4e4f534a:document=json.loads(chunk.decode('utf-8'))
            elif kind==0x004e4942:binary=chunk
            cursor+=8+length
        def positions(index):
            accessor=document['accessors'][index];view=document['bufferViews'][accessor['bufferView']]
            assert accessor['componentType']==5126 and accessor['type']=='VEC3' and view.get('buffer',0)==0
            offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)
            return np.ndarray((accessor['count'],3),dtype='<f4',buffer=binary,offset=offset,strides=(view.get('byteStride',12),4)).astype(float)
        def indices(index):
            a=document['accessors'][index];v=document['bufferViews'][a['bufferView']]
            dtype=np.dtype({5121:'u1',5123:'<u2',5125:'<u4'}[a['componentType']])
            return np.ndarray((a['count'],),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dtype.itemsize),)).astype(int)
        image_pixels={}
        for idx,im in enumerate(document.get('images',[])):
            self.check('GLB image '+str(idx)+' embedded PNG', 'uri' not in im and im.get('mimeType')=='image/png')
            view=document['bufferViews'][im['bufferView']];off=view.get('byteOffset',0)
            raw=binary[off:off+view['byteLength']]
            with Image.open(BytesIO(raw)) as png:
                self.check('GLB image '+str(idx)+'2K dimensions', png.size==(2048,2048),list(png.size),[2048,2048])
                image_pixels[idx]=np.asarray(png.convert('RGB'))
        self.check('GLB all resources embedded',all('uri' not in b for b in document.get('buffers',[])))
        self.check('GLB excludes studio cameras lights',not document.get('cameras') and 'KHR_lights_punctual' not in document.get('extensions',{}))
        material_records={}
        def pixels(info):return image_pixels[document['textures'][info['index']]['source']]
        for mat in document.get('materials',[]):
            name=mat.get('name');pbr=mat.get('pbrMetallicRoughness',{});ext=mat.get('extensions',{})
            transmission=ext.get('KHR_materials_transmission',{}).get('transmissionFactor',0)
            base=np.asarray(pbr.get('baseColorFactor',[1,1,1,1]))
            brightness=float(np.mean(pixels(pbr['baseColorTexture']))/255) if 'baseColorTexture' in pbr else float(np.mean(base[:3]))
            rough=float(np.mean(pixels(pbr['metallicRoughnessTexture'])[...,1])/255)*pbr.get('roughnessFactor',1) if 'metallicRoughnessTexture' in pbr else pbr.get('roughnessFactor',1)
            metallic=float(np.mean(pixels(pbr['metallicRoughnessTexture'])[...,2])/255)*pbr.get('metallicFactor',1) if 'metallicRoughnessTexture' in pbr else pbr.get('metallicFactor',1)
            material_records[name]={'transmission':transmission,'alpha':float(base[3]),'brightness_mean':brightness,'roughness_mean':rough,'metallic_mean':metallic}
            if name in ('matte_black_vinyl','tire_rubber','polycarbonate'):
                self.check(name+' actual nonmetal material',metallic<=.01,metallic,'at most .01')
            if name in ('matte_black_vinyl','black_painted_aluminium'):
                self.check(name+' actually black and opaque',brightness<.25 and base[3]==1 and transmission==0 and mat.get('alphaMode','OPAQUE')=='OPAQUE',material_records[name])
            if name=='matte_black_vinyl':self.check('Black sheet finish actually matte',rough>=.6,rough,'at least .6')
            if name=='polycarbonate':
                self.check('Polycarbonate actually clear transmission',transmission>=.9 and rough<=.1 and 'baseColorTexture' not in pbr and pbr.get('metallicFactor',1)==0,material_records[name])
        def node_matrix(node):
            if 'matrix' in node:return np.asarray(node['matrix']).reshape(4,4).T
            x,y,z,w=node.get('rotation',[0,0,0,1])
            rotation=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                               [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                               [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
            result=np.eye(4);result[:3,:3]=rotation@np.diag(node.get('scale',[1,1,1]));result[:3,3]=node.get('translation',[0,0,0])
            return result
        to_ros=np.array([[1,0,0],[0,0,-1],[0,1,0]])
        found={};allpoints=[];mesh_count=0
        def visit(index,parent):
            nonlocal mesh_count
            node=document['nodes'][index];world=parent@node_matrix(node)
            if 'mesh' in node:
                mesh_count+=1
                extras=node.get('extras',{});key=(extras.get('source_link'),extras.get('source_part_name'))
                self.check('GLB mesh has source component '+node.get('name',''),key in self.component_world_bounds)
                pointsets=[]
                for primitive in document['meshes'][node['mesh']]['primitives']:
                    p=positions(primitive['attributes']['POSITION'])
                    tri=p[indices(primitive['indices']).reshape(-1,3)]
                    area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)
                    self.check('GLB nondegenerate triangles '+str(key),np.all(area>=1e-18),int(np.sum(area<1e-18)),0)
                    mat=document['materials'][primitive['material']]['name'];partname=key[1] or ''
                    expected=None
                    if partname.startswith(('front_door_','side_-1_','side_1_')) or partname=='rear_door_closed':expected='matte_black_vinyl'
                    elif partname.startswith('polycarbonate_floor_') or partname=='camera_shelf':expected='polycarbonate'
                    elif partname.startswith(('post_','rail_x_','rail_y_')):expected='black_painted_aluminium'
                    if expected:self.check('GLB prescribed material '+str(key),mat==expected,mat,expected)
                    pointsets.append((p@world[:3,:3].T+world[:3,3])@to_ros.T)
                p=np.concatenate(pointsets);allpoints.append(p)
                if key in self.component_world_bounds:
                    self.check('GLB component unique '+str(key),key not in found)
                    found[key]=index
                    self.near('GLB metres/axis conversion matches STL '+str(key),[p.min(0),p.max(0)],self.component_world_bounds[key],3e-7)
            for child in node.get('children',[]):visit(child,world)
        scene=document['scenes'][document.get('scene',0)]
        for index in scene.get('nodes',[]):visit(index,np.eye(4))
        self.check('GLB contains all robot components and no studio meshes',set(found)==set(self.component_world_bounds) and mesh_count==len(found),mesh_count,len(self.component_world_bounds))
        p=np.concatenate(allpoints)
        return {'path':str(path),'sha256':digest(path),'component_mesh_nodes':mesh_count,'bounds_in_ros_metres':[p.min(0).tolist(),p.max(0).tolist()],'actual_materials':material_records}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=None)
    ap.add_argument('--final',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--source-only',action='store_true')
    args=ap.parse_args()
    args.source=args.source or args.final/'underbot_description'
    audit=Audit(); audit.design(args.source)
    audit.source_manifest_hash=digest(args.source/'config/geometry_manifest.json')
    urdf=audit.urdf(args.source/'urdf/underbot.urdf')
    if args.source_only:
        print(json.dumps({'status':'PASS' if not audit.errors else 'FAIL','checks':len(audit.checks),'errors':audit.errors,'source_urdf':urdf},indent=2))
        return int(bool(audit.errors))
    meshes=audit.exports(args.final)
    glb=audit.glb(args.final)
    report={'status':'PASS' if not audit.errors else 'FAIL',
            'scope':'Independent actual digital geometry, STL topology, SI/mm transforms, GLB prescribed materials and URDF inertia/axis audit. No hardware certification or native simulator claim.',
            'final_urdf':urdf,'accepted_floor_and_frame_mm':[200,200],
            'accepted_covered_body_mm':[204,204],'check_count':len(audit.checks),'errors':audit.errors,
            'notes':audit.notes,'exports':meshes,'textured_glb':glb,'checks':audit.checks}
    output=args.final/'validation';output.mkdir(exist_ok=True)
    (output/'independent_geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    bounds=np.asarray(meshes['assembled_bounds_m']);span=(bounds[1]-bounds[0])*1000
    md=[f'# R10 independent dimensional audit: {report["status"]}',
        '',report['scope'],'',f'{len(audit.checks)} checks; {len(audit.errors)} failures.',
        '',f'- Actual floor and frame envelope: 200 × 200 mm. Accepted covered body: 204 × 204 mm.',
        '- Four posts: 20 × 20 × 500 mm. Sixteen rails: 160 mm cut length.',
        f'- Components: {meshes["component_count"]}; assembled STL triangles: {meshes["assembled_triangles"]:,}.',
        f'- Zero-pose full model envelope: {span[0]:.3f} × {span[1]:.3f} × {span[2]:.3f} mm, including base, arms and LiDAR.',
        '- Individual and assembled CAD STLs are millimetres; URDF visual STLs are metres. Actual triangle vertices were compared after transforms.',
        '- Actual stock chassis extent is compared with the published 558 × 404 × 205 mm envelope. Actual rear/front wheel diameters are compared with supplier dimensions 205/79 mm.',
        '- All four body covers are checked for opaque black material. Four clear polycarbonate floors and all black aluminium profiles are checked in the actual GLB.',
        '- R10 joint origins/axes, primitive collision geometry and positive physical inertia tensors are checked independently. Prior R08/R09 validation is not treated as proof for this revision.',
        '', '## Limits','', *[f'- {n}' for n in audit.notes]]
    if audit.errors:md+=['','## Failures','',*[f'- {e}' for e in audit.errors]]
    (output/'independent_geometry.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'checks':len(audit.checks),'errors':audit.errors,
                      'components':meshes['component_count'],'triangles':meshes['assembled_triangles']},indent=2))
    return int(bool(audit.errors))


if __name__=='__main__':
    raise SystemExit(main())
