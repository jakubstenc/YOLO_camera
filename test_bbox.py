import bpy
obj = bpy.data.objects["Rugged Box - Lid - 200x185x60"]
print(f"LID LOCATION: {obj.location}")
print(f"LID DIMENSIONS: {obj.dimensions}")
print(f"LID BOUNDING BOX:")
for v in obj.bound_box:
    print(f"  {v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f}")
