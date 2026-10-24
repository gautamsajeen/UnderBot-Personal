# Underbot R10 — corrected WR141E model

**200 × 200 mm transparent polycarbonate floors**, **black aluminium frame with 500 mm posts**, and **four matte-black plastic covers**. The 2 mm covers give a **204 × 204 mm body**, excluding projecting hinges and directly mounted arms. Four 20 × 20 mm posts leave a 160 mm clear opening; the sixteen horizontal rails are cut to 160 mm. Floors are 3 mm thick with post corner reliefs. The camera shelf is also clear polycarbonate.

![Actual R10 model render](docs/model_preview.png)

The WR141E uses the published **558 × 404 × 205 mm envelope**, supplier-listed **205 mm rear wheels** and a **79 mm single front wheel**. The contour, rear 40 mm tyre width, 334 mm track and 340 mm zero-pose wheelbase remain reconstructed estimates. The tower centre is proposed at X = −140 mm to clear the controls. The original mower orange/black finish is retained.

The Kinect casing is removed. Its internal arrangement is an unmeasured reservation, with an open optical aperture in the black front door. Each budget arm has five arm axes plus coupled gripper movement. Arm lengths, limits and torque ratings remain provisional. The GB70 is upright with its 222 mm dimension vertical. Wiring, bare-camera arrangement and mounting holes require hardware confirmation.

## Files

| File | Use |
|---|---|
| [Portable URDF](urdf/underbot.portable.urdf) | Direct import; relative metre-scale STL paths |
| [ROS URDF](urdf/underbot.urdf) / [Xacro](urdf/underbot.urdf.xacro) | Package mesh paths and modular source |
| [Textured URDF](urdf/underbot.textured.urdf) | Optional OBJ/MTL materials; importer dependent |
| [Gazebo profile](urdf/underbot.gazebo.urdf) | Optional controller/contact configuration |
| [Offline viewer](viewer.html) | Actual STL geometry, joint sliders and collisions |
| [Floor plan](docs/floor_plan_R10.svg) | Dimensioned tower plan |
| [Parameters](config/model_parameters.json) | Dimensions and evidence classification |
| [Validation](validation/final_verification.md) | Actual-file checks and limits |

Keep the entire package together. STL stores geometry only. The surrounding R10 export bundle contains a textured GLB, packed Blender scene and millimetre CAD STLs. The offline viewer displays simple URDF colours rather than PBR textures.

## ROS 2 / RViz2

Place this folder in a ROS 2 workspace's `src` directory, then run in a sourced ROS 2 shell:

```sh
colcon build --packages-select underbot_description --symlink-install
source install/setup.bash
ros2 launch underbot_description display.launch.py
```

For simulator feedback, use `publish_joint_states:=false use_sim_time:=true joint_states_topic:=/joint_states`. Follow the [import guide](docs/simulation_import.md) for Gazebo, Isaac Sim/Lab and Foxglove. Version-specific mimic handling matters.

## Physics and accuracy

There are **23 links and 22 joints**: four fixed, four continuous and fourteen arm/jaw revolute joints. Two jaws are mimic followers, leaving fourteen commanded coordinates and two passive caster coordinates. Four fixed-link merges leave nineteen bodies. The root is mobile, without a world attachment. Axes are X forward, Y left, Z up; camera optical axes are X right, Y down, Z forward. Equal positive rear-wheel rotation drives forward.

Assigned mass totals **19.5172478 kg**. The stock 9.1 kg mower baseline is split among chassis, wheels and caster; the added NOCO is separate. Massive links have explicit COM and positive physical inertia tensors based on declared approximations. There is no measured payload rating. The [accuracy register](docs/accuracy_and_physics.md) distinguishes user dimensions, published data and estimates.

Actual exported meshes, units, transforms and materials were independently checked. PyBullet checks compare mass, COM, full inertia and nonzero joint poses. MuJoCo covers rest, drive, turning, passive caster and coupled jaws. A 2,000-pose static audit bounds balance and estimated holding torque. Report hashes identify tested files. Native RViz2, Gazebo, Isaac Sim/Lab and FreeCAD execution was unavailable; no such runtime validation is claimed.

Individual components are closed. The assembled visual model contains contacting/intersecting components and is not a Boolean-unioned printing solid. Physics uses separate collision primitives. [FreeCAD source](cad/README.md) reconstructs the underlying geometry with faceted mower surfaces; no generated FCStd/STEP is claimed.

## Rebuild

Edit parameters/source, run `scripts/generate_model.py`, then `scripts/prepare_simulation.py`. These recreate basic visuals. Follow the surrounding R10 bundle README to rebuild and integrate detailed Blender meshes before regenerating the viewer and validation. Running only the basic generator replaces the detailed meshes.
