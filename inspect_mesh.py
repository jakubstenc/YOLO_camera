import bpy
import mathutils

obj = bpy.data.objects['rpicam_holder']
print("LOCATION:", obj.location)
print("BBOX:", [list(v) for v in obj.bound_box])

# Find the center of the bounding box
bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
center = sum(bbox_corners, mathutils.Vector()) / 8
print("BBOX CENTER:", center)

# Dimensions
print("DIMENSIONS:", obj.dimensions)
