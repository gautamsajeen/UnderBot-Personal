# R10 corrected geometry and physical model

R10 supersedes R09's approximate mower exterior. It corrects the rounded WR141E shell, rear hatch, coarse dark wheels, asymmetric guard and control placement using online references. The whole mower envelope is 558 × 404 × 205 mm. Supplier-supported wheel diameters are 205 mm rear and 79 mm front. Unpublished axle positions, tyre width, surface contours and mounting interfaces remain explicit estimates.

The tower retains 200 × 200 mm floors and frame, a 204 × 204 mm covered body and four 500 mm posts. The frame is black aluminium, all four vertical covers are opaque matte-black plastic, and internal floors plus the camera shelf are transparent polycarbonate. The proposed tower centre is X−140 mm to clear the mower controls.

This revision changes geometry, collisions, mass distribution and physical parameters. Earlier R08/R09 checks do not certify R10. The refreshed validation reports identify their exact input URDF and mesh hashes. Total model mass is 19.5172478 kg, based partly on unmeasured hardware allocations.

The package generator defines links, joints, collisions and mass/inertia plus the source geometry manifest. The supplied R10 Blender builder creates the detailed visual meshes and textured exports. Rebuilding only the basic generator will not reproduce the detailed final visual assets. Rebuild physical sources, detailed visuals, integration and validation together after changing dimensions.

See `accuracy_and_physics.md` for evidence classes, `physics_review.md` for limited numerical findings, and `simulation_import.md` for application setup. No manufacturer CAD, native simulator certification, measured payload or fully verified bare-Kinect fit is claimed.
