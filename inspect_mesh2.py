import bpy
import mathutils

obj = bpy.data.objects['rpicam_holder']
matrix = obj.matrix_world
bbox = [matrix @ mathutils.Vector(v) for v in obj.bound_box]

min_x = min(v.x for v in bbox)
max_x = max(v.x for v in bbox)
min_y = min(v.y for v in bbox)
max_y = max(v.y for v in bbox)
min_z = min(v.z for v in bbox)
max_z = max(v.z for v in bbox)

print(f"WORLD BBOX:")
print(f"  X: {min_x:.2f} to {max_x:.2f} (Center: {(min_x+max_x)/2:.2f}, Width: {max_x-min_x:.2f})")
print(f"  Y: {min_y:.2f} to {max_y:.2f} (Center: {(min_y+max_y)/2:.2f}, Depth: {max_y-min_y:.2f})")
print(f"  Z: {min_z:.2f} to {max_z:.2f} (Center: {(min_z+max_z)/2:.2f}, Height: {max_z-min_z:.2f})")
