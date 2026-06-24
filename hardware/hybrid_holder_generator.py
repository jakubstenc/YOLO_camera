import bpy
import mathutils
import math
import os

# ==============================================================================
# Configuration Variables
# ==============================================================================
TARGET_MESH_NAMES = ["CameraHolder", "rpicam_holder"]
PERFECT_MOUNT_STL = "box_blender_files/camera_holder/Pi_CAM_BACK_v2.stl"
OUTPUT_FILENAME = "odseven_hybrid_holder.stl"

# --- Gutting (Cutout) Variables ---
# Dimensions of the block used to destroy the old inner mounting posts.
CUTOUT_WIDTH = 50.0   # X dimension (mm)
CUTOUT_DEPTH = 30.0   # Y dimension (mm)
CUTOUT_HEIGHT = 20.0  # Z dimension (mm) - tall enough to cut completely through

# Offsets to shift the cutout block so it DOES NOT cut through the outer frame walls!
CUTOUT_OFFSET_X = 0.0
CUTOUT_OFFSET_Y = 5.0  # Shift it to avoid cutting the outer walls
CUTOUT_OFFSET_Z = 0.0

# --- Imported Mount Alignment Variables ---
# Tweak these to slide the imported mount perfectly into the hollowed frame.
MOUNT_OFFSET_X = 0.0
MOUNT_OFFSET_Y = 0.0
MOUNT_OFFSET_Z = 0.0

# Tweak these to rotate the imported mount so it faces the correct way! (in degrees)
MOUNT_ROTATION_X = 90.0
MOUNT_ROTATION_Y = 0.0
MOUNT_ROTATION_Z = 0.0

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

def import_stl(filepath):
    try:
        bpy.ops.wm.stl_import(filepath=filepath)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=filepath)
    return bpy.context.selected_objects[0]

# ==============================================================================
# Main Execution
# ==============================================================================
def main():
    print("\n--- Starting Digital Kitbash Script ---")
    
    holder_obj = None
    for name in TARGET_MESH_NAMES:
        if name in bpy.data.objects:
            holder_obj = bpy.data.objects[name]
            print(f"Found target outer frame: '{name}'")
            break
            
    if holder_obj is None:
        print(f"ERROR: Could not find target meshes {TARGET_MESH_NAMES}")
        return
        
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Bounding box center
    bbox = [holder_obj.matrix_world @ mathutils.Vector(v) for v in holder_obj.bound_box]
    center_x = (min(v.x for v in bbox) + max(v.x for v in bbox)) / 2.0
    center_y = (min(v.y for v in bbox) + max(v.y for v in bbox)) / 2.0
    center_z = (min(v.z for v in bbox) + max(v.z for v in bbox)) / 2.0
    
    # 1. Gut the Original
    print(f"1/3: Hollowing out the center ({CUTOUT_WIDTH}x{CUTOUT_DEPTH}mm)...")
    cutout_block = create_block(
        name="GuttingBlock", 
        dimensions=(CUTOUT_WIDTH, CUTOUT_DEPTH, CUTOUT_HEIGHT),
        location=(
            center_x + CUTOUT_OFFSET_X, 
            center_y + CUTOUT_OFFSET_Y, 
            center_z + CUTOUT_OFFSET_Z
        )
    )
    apply_boolean(holder_obj, cutout_block, operation='DIFFERENCE')
    
    # 2. Import & Position
    print(f"2/3: Importing '{PERFECT_MOUNT_STL}' and positioning...")
    import_path = os.path.abspath(PERFECT_MOUNT_STL)
    if not os.path.exists(import_path):
        print(f"ERROR: Could not find '{import_path}'")
        return
        
    perfect_mount = import_stl(import_path)
    
    # Apply Rotations
    perfect_mount.rotation_euler = (
        math.radians(MOUNT_ROTATION_X),
        math.radians(MOUNT_ROTATION_Y),
        math.radians(MOUNT_ROTATION_Z)
    )
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    # Apply Location
    perfect_mount.location = (
        center_x + MOUNT_OFFSET_X,
        center_y + MOUNT_OFFSET_Y,
        center_z + MOUNT_OFFSET_Z
    )
    
    # 3. Weld
    print("3/3: Welding the inner mount to the hollowed outer frame...")
    apply_boolean(holder_obj, perfect_mount, operation='UNION')
    
    # 4. Export
    print(f"Exporting final hybrid holder to '{OUTPUT_FILENAME}'...")
    bpy.ops.object.select_all(action='DESELECT')
    holder_obj.select_set(True)
    bpy.context.view_layer.objects.active = holder_obj
    
    output_path = os.path.abspath(OUTPUT_FILENAME)
    try:
        try:
            bpy.ops.wm.stl_export(filepath=output_path, export_selected_objects=True)
        except AttributeError:
            bpy.ops.export_mesh.stl(filepath=output_path, use_selection=True)
        print(f"SUCCESS: Saved to {output_path}")
    except Exception as e:
        print(f"ERROR during export: {e}")

if __name__ == "__main__":
    main()
