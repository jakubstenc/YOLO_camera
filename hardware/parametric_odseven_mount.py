import bpy
import mathutils
import os

# ==============================================================================
# Parametric OdSeven Mount Generator
# ==============================================================================
TARGET_MESH_NAMES = ["CameraHolder", "rpicam_holder"]
OUTPUT_FILENAME = "odseven_perfect_mount.stl"

# 1. Gutting Variables (To destroy the old uneven posts and narrow bridge)
GUT_WIDTH = 64.0   # Clear out a huge 64mm wide section in the middle
GUT_DEPTH = 35.0   # Clear out the Y depth
GUT_HEIGHT = 20.0  # Clear out the Z thickness
GUT_OFFSET_Y = 2.0 # Push gutting slightly forward if needed

# 2. The New "Perfect Bed" Bridge
BRIDGE_WIDTH = 68.0   # Wide enough to connect the gutted arms
BRIDGE_DEPTH = 25.0   # Tall enough to hold the 21mm Y-spaced screws
BRIDGE_HEIGHT = 4.0   # Thickness of the new flat mounting plate

# 3. The Lens/IR Window (Cut out of the new bridge)
WINDOW_WIDTH = 50.0   # 50mm wide window allows all 3 lenses to look through
WINDOW_DEPTH = 15.0   # 15mm tall window
WINDOW_HEIGHT = 20.0  # Cut completely through the bridge

# 4. The Screw Holes
HOLE_SPACING_X = 55.0
HOLE_SPACING_Y = 21.0
HOLE_DIAMETER = 2.2

# ==============================================================================
# Helper Functions
# ==============================================================================
def apply_boolean(target_obj, mod_obj, operation='UNION'):
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
    print("\n--- Generating Parametric OdSeven Mount ---")
    
    # Locate Target Frame
    holder_obj = None
    for name in TARGET_MESH_NAMES:
        if name in bpy.data.objects:
            holder_obj = bpy.data.objects[name]
            break
            
    if holder_obj is None:
        print(f"ERROR: Target mesh not found.")
        return
        
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Bounding box center
    bbox = [holder_obj.matrix_world @ mathutils.Vector(v) for v in holder_obj.bound_box]
    center_x = (min(v.x for v in bbox) + max(v.x for v in bbox)) / 2.0
    center_y = (min(v.y for v in bbox) + max(v.y for v in bbox)) / 2.0
    center_z = (min(v.z for v in bbox) + max(v.z for v in bbox)) / 2.0
    
    # 1. GUT THE OLD MOUNT
    print("1/4: Gutting old uneven geometry...")
    gut_block = create_block("GutBlock", (GUT_WIDTH, GUT_DEPTH, GUT_HEIGHT), 
                             (center_x, center_y + GUT_OFFSET_Y, center_z))
    apply_boolean(holder_obj, gut_block, operation='DIFFERENCE')
    
    # 2. CREATE THE NEW PERFECT BED
    print("2/4: Inserting perfect flat bridge...")
    bridge = create_block("PerfectBridge", (BRIDGE_WIDTH, BRIDGE_DEPTH, BRIDGE_HEIGHT),
                          (center_x, center_y, center_z))
                          
    # 3. CUT THE LENS WINDOW
    print("3/4: Cutting IR & Lens window...")
    window = create_block("LensWindow", (WINDOW_WIDTH, WINDOW_DEPTH, WINDOW_HEIGHT),
                          (center_x, center_y, center_z))
    apply_boolean(bridge, window, operation='DIFFERENCE')
    
    # 4. DRILL SCREW HOLES
    print("4/4: Drilling 55x21mm holes...")
    dx = HOLE_SPACING_X / 2.0
    dy = HOLE_SPACING_Y / 2.0
    hole_locs = [
        (center_x + dx, center_y + dy, center_z),
        (center_x - dx, center_y + dy, center_z),
        (center_x + dx, center_y - dy, center_z),
        (center_x - dx, center_y - dy, center_z)
    ]
    for i, loc in enumerate(hole_locs):
        cutter = create_cylinder(f"Hole_{i}", HOLE_DIAMETER, 20.0, loc)
        apply_boolean(bridge, cutter, operation='DIFFERENCE')
        
    # Weld bridge to holder
    apply_boolean(holder_obj, bridge, operation='UNION')
    
    # Export
    bpy.ops.object.select_all(action='DESELECT')
    holder_obj.select_set(True)
    bpy.context.view_layer.objects.active = holder_obj
    
    output_path = os.path.abspath(OUTPUT_FILENAME)
    try:
        try:
            bpy.ops.wm.stl_export(filepath=output_path, export_selected_objects=True)
        except:
            bpy.ops.export_mesh.stl(filepath=output_path, use_selection=True)
        print(f"SUCCESS: Saved to {output_path}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
