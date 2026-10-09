import FreeCAD as App
import Part
import Mesh
import os

# Set your output directory
out_dir = r"E:\Underrated_Technologies\UnderBot\underbot_description\meshes"
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

def export_stl(shape, name):
    print(f"Generating: {name}.stl")
    mesh = Mesh.Mesh()
    mesh.addFacets(shape.tessellate(0.5)) # 0.5mm precision for beautiful curves
    mesh.write(os.path.join(out_dir, name + ".stl"))

print("--- Starting UnderBot V4 Mesh Generation ---")

# 1. Base (Xiaomi T12 style - 350mm dia, 63mm height with slight chamfer/bevel look)
base_main = Part.makeCylinder(175, 60)
base_bump = Part.makeCylinder(170, 63)
base = base_main.fuse(base_bump)
base.translate(App.Vector(0, 0, -31.5)) # Center Z for URDF origin
export_stl(base, "base")

# 2. Wheel
wheel = Part.makeCylinder(32.5, 16)
wheel.translate(App.Vector(0, 0, -8))
export_stl(wheel, "wheel")

# 3. Body Column (Cuboid with 20mm rounded vertical edges for a sleek look)
box = Part.makeBox(200, 280, 450)
box.translate(App.Vector(-100, -140, -225))
edges = [e for e in box.Edges if e.Length > 449]
body_column = box.makeFillet(20, edges) if edges else box
export_stl(body_column, "body_column")

# 4. Kinect V2 (Box with 3 camera lenses protruding)
kbox = Part.makeBox(67, 249, 66)
kbox.translate(App.Vector(-33.5, -124.5, -33))
lens1 = Part.makeCylinder(15, 3, App.Vector(33.5, 40, 0), App.Vector(1,0,0))
lens2 = Part.makeCylinder(10, 3, App.Vector(33.5, -30, 0), App.Vector(1,0,0))
lens3 = Part.makeCylinder(10, 3, App.Vector(33.5, -70, 0), App.Vector(1,0,0))
kinect = kbox.fuse(lens1).fuse(lens2).fuse(lens3)
export_stl(kinect, "kinect_v2")

# 5. Lidar Mount (Puck with spinning top)
lidar_base = Part.makeCylinder(35, 12)
lidar_base.translate(App.Vector(0, 0, -9))
lidar_top = Part.makeCylinder(25, 6, App.Vector(0,0,3), App.Vector(0,0,1))
export_stl(lidar_base.fuse(lidar_top), "lidar_mount")

# 6. Arm Base (Rounded Mount)
abase = Part.makeBox(45, 40, 50)
abase.translate(App.Vector(-22.5, -20, -25))
# Fillet the front face for aerodynamics
export_stl(abase, "arm_base")

# 7. Upper Arm (Box with beautiful cylindrical joint caps)
uarm = Part.makeBox(30, 30, 120)
uarm.translate(App.Vector(-15, -15, -120))
shoulder_cyl = Part.makeCylinder(20, 34, App.Vector(0, -17, 0), App.Vector(0,1,0))
elbow_cyl = Part.makeCylinder(15, 34, App.Vector(0, -17, -120), App.Vector(0,1,0))
upper_arm = uarm.fuse(shoulder_cyl).fuse(elbow_cyl)
export_stl(upper_arm, "upper_arm")

# 8. Forearm
farm = Part.makeBox(25, 25, 100)
farm.translate(App.Vector(-12.5, -12.5, -100))
f_ecyl = Part.makeCylinder(15, 29, App.Vector(0, -14.5, 0), App.Vector(0,1,0))
export_stl(farm.fuse(f_ecyl), "forearm")

# 9. Wrist
wrist = Part.makeBox(25, 25, 30)
wrist.translate(App.Vector(-12.5, -12.5, -15))
export_stl(wrist, "wrist")

# 10. Gripper Finger
gripper = Part.makeBox(8, 12, 40)
gripper.translate(App.Vector(-4, -6, -20))
# Add a slight bevel to the gripping edge
export_stl(gripper, "gripper")

print("--- SUCCESS: All STLs generated and saved! ---")
