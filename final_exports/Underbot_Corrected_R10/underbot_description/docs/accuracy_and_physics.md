# R10 dimensions, materials and evidence

R10 corrects the WR141E exterior and wheel geometry and uses four opaque matte-black plastic vertical covers. The aluminium frame is black. The four internal floor plates and the camera shelf are transparent polycarbonate. The user-defined dimensions below are exact modelling targets; online component specifications and unmeasured installation proposals are identified separately. Geometry checks establish consistency with these targets, not a dimensional survey of the real hardware.

All dimensions in this table are millimetres. Coordinates use X forward, Y left and Z up, with the mower envelope centred in X/Y and ground at Z0.

| Item | R10 geometry | Evidence / status |
|---|---|---|
| WR141E whole-product envelope | 558 L × 404 W × 205 H | Published by Worx; moulded contours are image-derived approximations |
| Frame and floor bounds | 200 × 200 | User requirement |
| Covered body | 204 × 204 | User-approved external 2 mm flat covers; hinges and arm carriers project locally |
| Clear opening between posts | 160 × 160 | Derived from 20 mm profiles |
| Vertical posts | 4 × 20 × 20 × 500, Z205–705 | User stock; vertical mounting datum proposed |
| Horizontal rails | 16 × 160 long | Cut from the user's 200 mm stock to achieve 200 mm outside frame size |
| Floor plates | 200 × 200 × 3, with four 20 × 20 corner reliefs | Transparent polycarbonate; thickness proposed; net area 0.0384 m² each |
| Floor tops | Z228, 503, 578, 708 | Plates sit on four 20 mm high rail rings |
| Tower centre | X−140, Y0 | Proposed rearward installation to clear the original controls; mounting holes unmeasured |
| Four vertical covers | 2 mm opaque matte-black plastic, Z225–685 | Front, rear and both sides black; front has an open optical aperture |
| Front/rear cover centre planes | X−39 / −241 | Inner faces X−40 / −240; 200 mm sheet width |
| Side cover centre planes | Y±101 | Inner faces Y±100; 200 mm sheet depth |
| Arm roots | X−140, Y±108, Z545 | Proposed carriers attached to the aluminium structure |
| Rear drive tyres | Ø205 × 40; centres (−170, ±167, 102.5) | Diameter from exact-part supplier; width and centre locations estimated |
| Rear track / nominal wheelbase | 334 / 340 | Image-derived estimates; wheelbase uses caster roll centre at zero swivel |
| Front caster | Ø79 × 55; roll centre (+170, 0, 39.5) at zero swivel | Diameter from exact-part supplier; width approximately 55 from another supplier |
| Caster swivel / trail | (+190, 0, 110) / 20 | Unmeasured geometry estimates; wheelbase varies with swivel |
| GB70 upright body | 69 D × 99 W × 222 H, bottom Z232 | Manufacturer body dimensions rotated; orientation proposed |
| GB70 installation reservation | 70 D × 152 W × 222 H | Published overall envelope rotated; leaves 4 mm each side within the 160 mm opening |
| Bare camera reservation | 70 D × 156 W × 56 H, link datum (−75, 0, 635) | Unmeasured packaging proposal, **not Kinect PCB dimensions** |
| Camera shelf | 80 D × 156 W × 3, top Z601.5 | Transparent polycarbonate; supporting hangers remain black aluminium |
| Camera optical aperture | 156 W × 59.5 H, Z603–662.5 | Open aperture; no plastic sheet across the optical path |
| Optical frame local offset | (34, 69.25, 6.5) from camera link | Uncalibrated depth-lens datum |
| Arm segment lengths | 105 / 90 / 45 / 25 / 50 | Upper arm / forearm / wrist / hand / finger; budget-kit approximations |
| LiDAR | Ø70 × 45, Z733–778 | Unspecified model; placeholder geometry |

The 204 mm body envelope concerns the four flat covers. It does not include the side arms, hinges, bolts or other projecting hardware. Covers meet the 200 mm floor bounds; floor corner reliefs clear the posts. The service door is represented fixed closed. All internal floor plates remain clear even though the closed opaque covers conceal them.

## Online evidence

The [Worx WR141E product table](https://eu.worx.com/en/robot-mower-landroid-s-robot-mower-for-lawns-up-to-400-m2-wr141e/) gives the 558 × 404 × 205 envelope, one front wheel and 9.1 kg with battery. Its current heading incorrectly says S400; the model identifier and supplied-product entry specify WR141E / M500. The [original WR141E manual](https://cdn2.hubspot.net/hubfs/5237793/User%20Manual/Landroid%20M%202019/User_Manual_WR141E_EN.pdf) instead lists 8.5 kg machinery weight. Neither source gives a stripped chassis mass, axle drawing or inertia tensor.

The [model-specific exploded parts list](https://media.adeo.com/media/5418924/media.pdf) maps rear wheel 50024699 and front assembly 50036897 to WR141E. The original-part supplier lists [205 mm rear diameter](https://www.clasohlson.com/no/Hjul-Bakre-Worx-Landroid/p/51-2138) and [79 mm front diameter](https://www.clasohlson.com/no/Hjul-fremre-Worx-Landroid-Landxcape/p/51-3393). Another supplier gives [approximately 55 mm front width](https://sklep.letmerepair.pl/pl/p/WORX-Przednie-kolo-do-kosiarki-autonomicznej-50036897/803). Stock rear tyre width, track, wheelbase and trail were not found in reliable dimensioned publications. A 40 mm shipping-package thickness is not a tyre-width specification. The model's 40 mm rear width remains an estimate.

The orange rounded nose, sloping shoulders, black rear hatch, asymmetric right-front guard, coarse tyres, dark wheel faces and control placement follow photographs and the manual. Their surface coordinates, tread pattern and decorative details are inferred, not manufacturer CAD. In the ROS convention, charging contacts and height dial are on negative Y; STOP and display are on positive Y. Correcting the overall envelope alone would not establish these details.

NOCO dimensions come from [GB70 specifications](https://no.co/gb70/specs) and the [manufacturer drawing](https://no.co/media/wysiwyg/downloads/brochures/Boost/GB70_Data_Sheet_12.05.2024.pdf). The upright layout, restraint and cable clearances are proposed installation details. The budget arm reference is Tatiy Amazon.de B0B4VKYQ6S; no trustworthy dimensioned pivot drawing or continuous servo rating was available. Each arm represents five positioning axes plus one coupled gripper input, matching the accepted budget-kit choice.

## Bare Kinect and unspecified electronics

The 249 mm external Kinect case is excluded, as requested. The bare board, thermal parts, optics and cables are illustrative reservations. Case removal alone does not establish that the real hardware fits a 160 mm clear opening. The 150 mm board width, 138.5 mm optical separation and component locations are unmeasured. The [iFixit teardown](https://www.ifixit.com/Teardown/Xbox+One+Kinect+Teardown/19725) identifies components but does not substantiate those proposed dimensions. The 0.970 kg camera allocation is retained bookkeeping, not measured bare-electronics mass.

The optical frame uses X right, Y down, Z forward and RPY (−π/2, 0, −π/2), looking along body +X, consistent with [ROS REP-103](https://www.ros.org/reps/rep-0103.html). Position and intrinsic calibration remain provisional. The model supplies no functioning RGB/depth/LiDAR observations. Exact converter, LiDAR, compute hardware and solar-panel specifications remain unconfirmed; their illustrated shapes do not verify electrical, thermal or solar-power performance.

## Joints, collisions and mass

The URDF has 23 links and 22 joints: four fixed, four continuous and fourteen revolute. Two revolute jaws are mimic followers. Fourteen independent commands comprise two drive wheels and six inputs per arm; two further independent coordinates belong to the passive caster. Both rear wheel axes are +Y. Caster swivel is +Z and roller motion is +Y. Mirrored arm roots and axes use proper rotations. The gripper followers use their authored opposite axes and a mimic multiplier of 1.

The folded zero origins are shoulder −150°, elbow +60°, wrist −60°. Proposed command ranges are base ±45°, shoulder/elbow ±20°, wrist pitch ±30°, wrist roll ±90°, and gripper 0–0.6 rad. These are modelling limits, not measured servo hard stops or proof of a collision-free simultaneous workspace. Simplified collision geometry is separate from detailed visual meshes.

The R10 inertials sum to **19.5172478 kg**. The stock baseline is 9.1 kg, divided into 7.35 kg fixed chassis, two 0.75 kg rear wheels, 0.15 kg fork and 0.10 kg caster. These component allocations and installed mass distribution are estimated. GB70 mass is allocated 1.9 kg. Inertias combine component approximations using rotated tensors and the parallel-axis theorem; shaped mower parts use bounding-box inertia proxies. Profile linear mass and material densities are assumed. Removing physical mower parts requires revising this budget.

Proposed effort caps are 2.5 N·m per drive wheel, 1 N·m per arm positioning joint and 0.3 N·m per gripper input. Wheel and arm speed limits are 4 and 1 rad/s. These do not establish actual motor ratings or payload. The sampled static audit reaches 0.944059 N·m at the right shoulder without payload, close to its assumed 1 N·m cap.

See `physics_review.md` and exact-source validation reports for performed checks. Native RViz2, Gazebo, Isaac Sim, Isaac Lab and FreeCAD runs are not claimed. Unpublished dimensions remain labelled estimates rather than being presented as online measurements.
