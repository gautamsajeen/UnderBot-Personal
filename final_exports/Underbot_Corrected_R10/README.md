# Underbot R10 corrected export

This revision corrects the WR141E reconstruction and implements **four black plastic covers**, **black aluminium profiles** and **transparent polycarbonate internal floors**. Floors/frame are **200 × 200 mm**, the covered body is **204 × 204 mm**, and posts are **500 mm long**. Two arms attach to frame brackets; the stripped Kinect reservation stays inside the tower.

![Actual exported R10 model](renders/Underbot_R10_hero.png)

| Deliverable | Contents and units |
|---|---|
| [URDF package](underbot_description/README.md) | ROS, portable and textured URDF; metre-scale link-local meshes, collisions and estimated inertias |
| [Assembled STL](stl/Underbot_R10_assembled_mm.stl) | Zero-pose assembly in millimetres; separate closed components |
| [Component STLs](stl/components_mm) | Part-local millimetres; transforms in geometry_export_manifest.json |
| [Link STLs](stl/links_local_mm) | Link-local millimetres; convert to metres before simulation |
| [Textured GLB](models/Underbot_R10_textured.glb) | Embedded 2048 px PBR maps; metres, glTF Y-up |
| [Blender scene](models/Underbot_R10_studio.blend) | Packed textures, link hierarchy and studio lighting |
| [Joint viewer](underbot_description/viewer.html) | Self-contained actual-STL inspector |
| [Floor plan](docs/floor_plan_R10.svg) | Tower dimensions and post clearances |

STL cannot store textures. Use GLB/Blender for full appearance and URDF for articulated simulation. The GLB has a posed hierarchy and joint metadata but is not itself a simulator articulation.

Published mower envelope: 558 × 404 × 205 mm. Supplier-supported rear/front wheel diameters: 205/79 mm. Unpublished axle spacing, contours, arm geometry, bare Kinect layout, actuator ratings and mass distribution remain estimates. See the [online reference register](docs/WR141E_reference_register.md), [wheel evidence](docs/wheel_dimension_evidence.json) and [accuracy register](underbot_description/docs/accuracy_and_physics.md). This is a documented simulation model, not a manufacturer digital twin.

## Review views

- [Rear](renders/Underbot_R10_rear.png): fourth black cover and frame.
- [Cutaway](renders/Underbot_R10_cutaway.png): front and one side removed to show clear floors and components.
- [Mower only](renders/Underbot_R10_base.png) and [top](renders/Underbot_R10_base_top.png): base without the tower.

## Verification

The [independent audit](validation/independent_geometry.md) checks actual triangles, topology, unit conversion, transforms, materials and URDF data. The [physics/import review](underbot_description/validation/final_verification.md) records authoring, Xacro, PyBullet, MuJoCo and static checks. Model mass is provisionally 19.5172478 kg. Review notes identify touching aggregate visual edges; individual components are closed, with separate collision primitives.

Native Gazebo, Isaac Sim/Lab, RViz2 and FreeCAD were not run. See the [version-aware import guide](underbot_description/docs/simulation_import.md). There is no universal required fixed-body count; merging and mimic support depend on the importer.

## Validation and reproduction

Python requires NumPy/Pillow; Xacro, MuJoCo and PyBullet are needed for their checks. Blender 4.5 LTS produced the export. From this folder:

```sh
python underbot_description/scripts/generate_model.py
python underbot_description/scripts/prepare_simulation.py
python scripts/build_R10_materials.py
blender --background --python scripts/build_R10_blender.py -- --skip-renders
python scripts/integrate_R10.py
python underbot_description/scripts/build_viewer.py
python scripts/verify_R10_geometry.py
python underbot_description/scripts/validate_model.py --report underbot_description/validation/authoring_checks.json
python underbot_description/scripts/validate_model.py underbot_description/urdf/underbot.portable.urdf --report underbot_description/validation/portable_checks.json
python underbot_description/scripts/check_sources.py
python underbot_description/scripts/verify_pybullet_import.py
python underbot_description/scripts/static_physics_audit.py
python underbot_description/scripts/physics_smoke_test.py
node scripts/verify_viewer_R10.cjs
blender --background models/Underbot_R10_studio.blend --python scripts/render_R10.py -- --output .
```

Regenerate delivery checksums after changes. The assembled STL has intentional interfaces; it is not a single Boolean-unioned printing solid. Use per-component files for part-specific work.
