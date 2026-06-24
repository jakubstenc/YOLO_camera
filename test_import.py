import bpy
try:
    bpy.ops.wm.step_import(filepath="dummy.step")
    print("wm.step_import exists")
except AttributeError:
    print("wm.step_import does not exist")

try:
    bpy.ops.import_scene.step(filepath="dummy.step")
    print("import_scene.step exists")
except AttributeError:
    print("import_scene.step does not exist")
