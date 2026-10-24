# R10 independent dimensional audit: PASS

Independent actual digital geometry, STL topology, SI/mm transforms, GLB prescribed materials and URDF inertia/axis audit. No hardware certification or native simulator claim.

6098 checks; 0 failures.

- Actual floor and frame envelope: 200 × 200 mm. Accepted covered body: 204 × 204 mm.
- Four posts: 20 × 20 × 500 mm. Sixteen rails: 160 mm cut length.
- Components: 293; assembled STL triangles: 250,452.
- Zero-pose full model envelope: 558.000 × 713.449 × 778.000 mm, including base, arms and LiDAR.
- Individual and assembled CAD STLs are millimetres; URDF visual STLs are metres. Actual triangle vertices were compared after transforms.
- Actual stock chassis extent is compared with the published 558 × 404 × 205 mm envelope. Actual rear/front wheel diameters are compared with supplier dimensions 205/79 mm.
- All four body covers are checked for opaque black material. Four clear polycarbonate floors and all black aluminium profiles are checked in the actual GLB.
- R10 joint origins/axes, primitive collision geometry and positive physical inertia tensors are checked independently. Prior R08/R09 validation is not treated as proof for this revision.

## Limits

- The floor/frame dimensions and accepted 204 mm covered body are user requirements. The 3 mm floors and 2 mm covers are proposed material thicknesses.
- WR141E 558 × 404 × 205 mm and upright GB70 body 69 × 99 × 222 mm are published envelopes. Replacement-part suppliers publish the 205 mm rear and 79 mm front wheel diameters; detailed chassis and battery contours remain reference-derived approximations.
- Rear tyre width 40 mm, track 334 mm, axle positions −170/+170 mm, caster trail 20 mm and approximate 55 mm caster width are online-reference estimates, not a factory dimensioned drawing.
- Bare Kinect layout, arm pivots/lengths, electronics, installed hardware masses, joint limits and motor ratings remain unmeasured design inputs. Mathematical mass/inertia checks do not certify actual hardware dynamics.
- The 140 mm rearward tower offset is a proposed mounting position intended to leave the controls accessible. Base attachment holes and structural load capacity are not measured or certified.
- Closed STL shells may overlap at fasteners/assembly interfaces. A watertight collection of shells is not a Boolean-unioned print-ready solid.
