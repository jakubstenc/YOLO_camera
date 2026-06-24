import FreeCAD
import Part
import Mesh

shape = Part.Shape()
shape.read('/home/meow/Documents/Antigravity/YOLO_camera/box_blender_files/camera_holder/Raspberry_Pi_Camera_OV5647_IR-CUT_175.step')
mesh = Mesh.Mesh()
mesh.addFacets(shape.tessellate(0.1))
mesh.write('/home/meow/Documents/Antigravity/YOLO_camera/perfect_mount.stl')
