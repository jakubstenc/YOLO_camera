import bpy
bpy.ops.wm.open_mainfile(filepath="box_blender_files/Box_bottom.blend")
target_obj = bpy.data.objects.get("Rugged Box - Box - 200x185x60")
if target_obj:
    print(f"BEFORE Verts: {len(target_obj.data.vertices)}")
    bpy.ops.mesh.primitive_cylinder_add(radius=6.25, depth=100.0, location=(target_obj.location.x+40, target_obj.location.y+40, target_obj.location.z))
    tool = bpy.context.active_object
    
    bool_mod = target_obj.modifiers.new(name="Vent_Boolean", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = tool
    bool_mod.solver = 'FLOAT'
    
    bpy.context.view_layer.objects.active = target_obj
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    print(f"AFTER FLOAT Verts: {len(target_obj.data.vertices)}")
