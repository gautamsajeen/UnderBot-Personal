# Independent physics smoke test

PASS - MuJoCo 3.15.0 imported the actual portable URDF.

Source SHA-256: `0daab387d38a86e5e90bae42bb30a04153d4ae816c9dd1822a9f1908ed1a9588`.
Declared / imported mass: 19.517247800 / 19.517247800 kg (estimated hardware inputs).
Motors: 14. Caster swivel and rolling joints are passive; all recorded ground contacts belong to the three intended rolling bodies.
Rest tilt: [-6.8451592487951264e-06, 0.04604351420298972] degrees; contacts: 6.
Resting COM: [-0.07986740834144347, 4.1229410701325394e-05, 0.29073247379972555] m in world coordinates; margin inside the actual ground support polygon: 0.0901 m.
Gentle forward translation: 0.0890 m.
Positive turn: 0.1935 rad.
Caster alignment transient: 0.0446 rad in the first 1.5 s. Final turn follows a 0.5 s ramp and 4 s hold at a commanded 0.25 rad/s; this is a sign and stability check, not accurate velocity tracking.
Maximum jaw-coupling error: 0.000016 rad.

| Commanded joint (both arms) | Target rad | Left / right achieved rad | Maximum final speed rad/s |
|---|---:|---:|---:|
| arm_base_joint | 0.100 | 0.097734 / 0.097736 | 0.000205 |
| shoulder_joint | 0.100 | 0.073902 / 0.073901 | 0.000065 |
| elbow_joint | 0.100 | 0.085367 / 0.085367 | 0.000003 |
| wrist_pitch_joint | 0.100 | 0.097131 / 0.097130 | 0.000000 |
| wrist_roll_joint | 0.100 | 0.100026 / 0.100026 | 0.000000 |

The adapter adds the ground, floating root and test motors. It verifies native jaw mimic constraints, only adds a relation if the importer omitted it, and uses an explicit 2 ms equality time constant for the ideal jaw coupling. It preserves the URDF mass, inertia and collision model. See physics_smoke.json for passive caster angles/rates, contact history, observed effort caps and exact configuration. The generated MJCF is a reproducible test scene, not an Isaac or Gazebo profile.

These tests validate import, numerical behavior and motion signs for this estimated model. They do not measure the real robot or prove payload capability, full-range collision freedom or compatibility with other engines.
