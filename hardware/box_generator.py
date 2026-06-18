import bpy
import bmesh
import math
import os

# ------------------------------------------------------------------------
# Configuration Variables (These are RELATIVE offsets from the center of the box!)
# ------------------------------------------------------------------------
VENT_LOCATION_OFFSET = (25.0, -104.0, 0.0)      # M12 vent offset relative to the Bottom (Side Wall)
CRADLE_LOCATION_OFFSET = (50.0, 50.0, 5.0)    # Pi Cradle offset relative to the Lid (Adjust Z to reach ceiling)

# ------------------------------------------------------------------------
# BOTTOM: Vent Hole Generation
# ------------------------------------------------------------------------
def generate_vent_hole(target_obj):
    """
    Creates a single M12 clearance hole (12.5mm diameter) and subtracts it.
    """
    print("Generating M12 vent hole for Bottom...")
    bpy.ops.object.select_all(action='DESELECT')
    
    hole_radius = 6.25
    hole_depth = 100.0
    
    # Calculate absolute position by adding the offset to the target object's location
    absolute_location = (
        target_obj.location.x + VENT_LOCATION_OFFSET[0],
        target_obj.location.y + VENT_LOCATION_OFFSET[1],
        target_obj.location.z + VENT_LOCATION_OFFSET[2]
    )
    
    bpy.ops.mesh.primitive_cylinder_add(radius=hole_radius, depth=hole_depth, location=absolute_location)
    tool = bpy.context.active_object
    tool.name = "M12_Vent_Cutout"
    
    # Rotate the cylinder 90 degrees around X to punch through the side wall horizontally
    tool.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.view_layer.objects.active = tool
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    # Ensure normals
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Boolean Difference
    bool_mod = target_obj.modifiers.new(name="Vent_Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = tool
    bool_mod.solver = 'FLOAT' # FLOAT prevents the mesh deletion bug that EXACT causes
    
    bpy.context.view_layer.objects.active = target_obj
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    
    # Cleanup tool
    bpy.data.objects.remove(tool, do_unlink=True)
    
    return "bottom_with_vents.stl"

# ------------------------------------------------------------------------
# TOP: Pi Cradle Generation
# ------------------------------------------------------------------------
def generate_pi_cradle(target_obj):
    """
    Generates a Pi Cradle for a 65x30x13mm aluminum case.
    Inner: 66x31mm. Outer: 69x34mm.
    Uses legs to attach to the Lid ceiling.
    """
    print("Generating Pi Cradle for Lid...")
    bpy.ops.object.select_all(action='DESELECT')
    
    # Dimensions
    inner_x, inner_y, inner_z = 66.0, 31.0, 14.0
    wall = 1.5
    outer_x = inner_x + (2 * wall)
    outer_y = inner_y + (2 * wall)
    outer_z = inner_z + wall  # Floor thickness = 1.5mm
    
    # 1. Outer Box (Main Cradle Body)
    # We place it at (0,0,0) and then move the final assembly
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    cradle = bpy.context.active_object
    cradle.scale = (outer_x, outer_y, outer_z)
    bpy.ops.object.transform_apply(scale=True)
    cradle.name = "Pi_Cradle_Base"
    
    # 2. Inner Pocket (Cutout)
    # We want the pocket to open facing the interior of the box (+Z)
    # So we offset the cut slightly UP (+wall/2.0), leaving a solid floor at the bottom (-Z).
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, wall/2.0))
    pocket = bpy.context.active_object
    pocket.scale = (inner_x, inner_y, inner_z + 1.0) # slightly taller to cut cleanly
    bpy.ops.object.transform_apply(scale=True)
    
    # 3. Thermal Windows (Side & Floor)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    thermal_x = bpy.context.active_object
    thermal_x.scale = (outer_x + 2, inner_y - 10, outer_z - 4)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    thermal_y = bpy.context.active_object
    thermal_y.scale = (inner_x - 10, outer_y + 2, outer_z - 4)
    bpy.ops.object.transform_apply(scale=True)
    
    # Floor thermal window
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, outer_z/2))
    thermal_z = bpy.context.active_object
    thermal_z.scale = (inner_x - 15, inner_y - 8, 5)
    bpy.ops.object.transform_apply(scale=True)
    
    # 4. SD Card Notch (on one 31mm edge)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(outer_x/2.0, 0, 0))
    sd_notch = bpy.context.active_object
    sd_notch.scale = (10, 15.0, outer_z + 2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Combine cutouts
    cutouts = [pocket, thermal_x, thermal_y, thermal_z, sd_notch]
    for cut in cutouts:
        bool_mod = cradle.modifiers.new(name="Cut", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = cut
        bool_mod.solver = 'FLOAT'
        bpy.context.view_layer.objects.active = cradle
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        bpy.data.objects.remove(cut, do_unlink=True)
        
    # 5. Legs (4 pillars, 5mm diameter)
    leg_radius = 2.5
    leg_length = 15.0 # Distance from cradle to the ceiling
    legs = []
    x_offset = (outer_x / 2) - leg_radius
    y_offset = (outer_y / 2) - leg_radius
    
    for lx in [-x_offset, x_offset]:
        for ly in [-y_offset, y_offset]:
            # Place legs pointing DOWN towards the ceiling
            # The solid floor is at -outer_z/2. Legs start there and go down.
            bpy.ops.mesh.primitive_cylinder_add(radius=leg_radius, depth=leg_length, location=(lx, ly, -(outer_z/2) - (leg_length/2)))
            legs.append(bpy.context.active_object)
            
    # Join legs to cradle
    for leg in legs:
        leg.select_set(True)
    cradle.select_set(True)
    bpy.context.view_layer.objects.active = cradle
    bpy.ops.object.join()
    
    # Rotate 90 degrees around Z to align lengthwise with the lid
    cradle.rotation_euler = (0, 0, math.radians(90))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    # Move entire cradle to desired relative location
    # Set Z to roughly +5 so the cradle floats above the ceiling, and the -15mm legs reach down into the ceiling
    cradle.location = (
        target_obj.location.x + CRADLE_LOCATION_OFFSET[0],
        target_obj.location.y + CRADLE_LOCATION_OFFSET[1],
        target_obj.location.z + 5.0 
    )
    
    # Fuse to lid
    bool_union = target_obj.modifiers.new(name="Cradle_Union", type='BOOLEAN')
    bool_union.operation = 'UNION'
    bool_union.object = cradle
    bool_union.solver = 'FLOAT'
    
    bpy.context.view_layer.objects.active = target_obj
    bpy.ops.object.modifier_apply(modifier=bool_union.name)
    
    bpy.data.objects.remove(cradle, do_unlink=True)
    
    return "top_with_pi_cradle.stl"

# ------------------------------------------------------------------------
# MAIN EXECUTION
# ------------------------------------------------------------------------
def main():
    bottom_name = "Rugged Box - Box - 200x185x60"
    top_name = "Rugged Box - Lid - 200x185x60"
    
    target_obj = None
    export_filename = ""
    
    # Detect which file is loaded
    if bottom_name in bpy.data.objects:
        target_obj = bpy.data.objects[bottom_name]
        export_filename = generate_vent_hole(target_obj)
    elif top_name in bpy.data.objects:
        target_obj = bpy.data.objects[top_name]
        export_filename = generate_pi_cradle(target_obj)
    else:
        print("ERROR: Neither Top nor Bottom objects were found in the current blend file.")
        print(f"Available: {[o.name for o in bpy.data.objects]}")
        return

    # Cleanup geometry
    print("Cleaning up geometry with WELD modifier...")
    weld_mod = target_obj.modifiers.new(name="Weld_Cleanup", type='WELD')
    weld_mod.merge_threshold = 0.001
    bpy.context.view_layer.objects.active = target_obj
    bpy.ops.object.modifier_apply(modifier=weld_mod.name)
    
    # Export everything as a single combined part
    export_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
    export_path = os.path.join(export_dir, export_filename)
    
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select all meshes so they are exported together into one STL
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            
    print(f"Exporting all combined objects to {export_path}...")
    try:
        # Blender 4.2+ API
        bpy.ops.wm.stl_export(filepath=export_path, export_selected_objects=True)
    except AttributeError:
        # Fallback for older Blender versions
        bpy.ops.export_mesh.stl(filepath=export_path, use_selection=True)
                
    print("Done exporting combined STL file!")

if __name__ == "__main__":
    main()
