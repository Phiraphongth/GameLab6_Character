# Exports the character mesh (no skeleton, T-pose) as FBX for the Mixamo auto-rigger.
#   blender --background Assets/Models/player6/character.blend --python Tools/blender/export_for_mixamo.py -- <out.fbx>
import sys

import bpy

out = sys.argv[sys.argv.index("--") + 1]
body = bpy.data.objects["Body"]
for m in list(body.modifiers):
    if m.type == "ARMATURE":
        body.modifiers.remove(m)
body.parent = None
bpy.data.objects.remove(bpy.data.objects["Armature"])
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={"MESH"},
                         path_mode="COPY", embed_textures=True, add_leaf_bones=False)
print("EXPORTED", out)
