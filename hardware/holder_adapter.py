import bpy
import mathutils
import os

# ==============================================================================
# Configuration Variables
# ==============================================================================
HOLDER_MESH_NAME = "rpicam_holder"

# --- IR Camera Clearance Variables ---
# Instead of paving over the center, we cut a wide window to ensure the IR domes
# and the central lens are not obstructed by the holder's plastic arms.
# The OdSeven is ~60mm wide. We cut a 48mm wide window, leaving enough plastic
# on the sides (at +/- 27.5mm) for the 55mm-spaced mounting screws.
CLEARANCE_WIDTH = 48.0   # X dimension
CLEARANCE_DEPTH = 24.0   # Y dimension (should be enough for the camera PCB height)
CLEARANCE_HEIGHT = 20.0  # Z dimension (to cut completely through the plastic)

# --- Drilling Variables ---
HOLE_SPACING_X = 55.0   # mm
HOLE_SPACING_Y = 21.0   # mm
HOLE_DIAMETER = 2.2     # mm (M2 screws)
HOLE_DEPTH = 20.0       # mm

# --- Offsets ---
# Adjust this if the camera needs to be shifted forward/backward along the arms
OFFSET_Y = 0.0          # mm

OUTPUT_FILENAME = "odseven_holder_adapted.stl"

# ==============================================================================
# Helper Functions
# ==============================================================================
def apply_boolean(target_obj, mod_obj, operation='DIFFERENCE'):
    bpy.context.view_layer.objects.active = target_obj
    bool_mod = target_obj.modifiers.new(name=f"Bool_{operation}", type='BOOLEAN')
    bool_mod.operation = operation
    bool_mod.object = mod_obj
    bool_mod.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    bpy.data.objects.remove(mod_obj, do_unlink=True)

def create_block(name, dimensions, location=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    block = bpy.context.active_object
    block.name = name
    block.scale = (dimensions[0], dimensions[1], dimensions[2])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return block

def create_cylinder(name, diameter, depth, location=(0, 0, 0)):
    radius = diameter / 2.0
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=depth, location=location)
    cyl = bpy.context.active_object
    cyl.name = name
    return cyl

# ==============================================================================
# Main Execution
# ==============================================================================
def main():
    print("\n--- Starting Holder Adaptation Script ---")
    
    if HOLDER_MESH_NAME not in bpy.data.objects:
        print(f"ERROR: Could not find object '{HOLDER_MESH_NAME}'")
        return
        
    holder_obj = bpy.data.objects[HOLDER_MESH_NAME]
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    holder_obj.select_set(True)
    bpy.context.view_layer.objects.active = holder_obj

    # Calculate true bounding box center in world space
    bbox = [holder_obj.matrix_world @ mathutils.Vector(v) for v in holder_obj.bound_box]
    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)
    min_z = min(v.z for v in bbox)
    max_z = max(v.z for v in bbox)
    
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0 + OFFSET_Y
    center_z = (min_z + max_z) / 2.0

    print(f"Calculated center: X={center_x:.2f}, Y={center_y:.2f}, Z={center_z:.2f}")
    
    # 1. Clearance (Cutout for IR domes and main lens)
    print(f"1/2: Cutting IR clearance window ({CLEARANCE_WIDTH}x{CLEARANCE_DEPTH}mm)...")
    clearance_block = create_block(
        name="ClearanceBlock", 
        dimensions=(CLEARANCE_WIDTH, CLEARANCE_DEPTH, CLEARANCE_HEIGHT),
        location=(center_x, center_y, center_z)
    )
    apply_boolean(holder_obj, clearance_block, operation='DIFFERENCE')
    
    # 2. Drilling (Create 4 hole cutters)
    print(f"2/2: Drilling 4 new holes (Spacing: {HOLE_SPACING_X}x{HOLE_SPACING_Y}mm)...")
    dx = HOLE_SPACING_X / 2.0
    dy = HOLE_SPACING_Y / 2.0
    
    hole_locations = [
        (center_x + dx, center_y + dy, center_z),
        (center_x - dx, center_y + dy, center_z),
        (center_x + dx, center_y - dy, center_z),
        (center_x - dx, center_y - dy, center_z),
    ]
    
    for i, loc in enumerate(hole_locations):
        cutter = create_cylinder(
            name=f"HoleCutter_{i+1}", 
            diameter=HOLE_DIAMETER, 
            depth=HOLE_DEPTH, 
            location=loc
        )
        apply_boolean(holder_obj, cutter, operation='DIFFERENCE')
        
    # 3. Export
    print(f"Exporting to '{OUTPUT_FILENAME}'...")
    bpy.ops.object.select_all(action='DESELECT')
    holder_obj.select_set(True)
    bpy.context.view_layer.objects.active = holder_obj
    
    output_path = os.path.abspath(OUTPUT_FILENAME)
    try:
        bpy.ops.wm.stl_export(filepath=output_path, export_selected_objects=True)
        print(f"SUCCESS: Saved to {output_path}")
    except Exception as e:
        print(f"ERROR during export: {e}")

if __name__ == "__main__":
    main()
