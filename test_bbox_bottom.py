import bpy
obj = bpy.data.objects["Rugged Box - Box - 200x185x60"]
print(f"BOTTOM DIMENSIONS: {obj.dimensions}")
print(f"BOTTOM BOUNDING BOX RELATIVE TO LOCATION:")
for v in obj.bound_box:
    print(f"  {v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f}")
