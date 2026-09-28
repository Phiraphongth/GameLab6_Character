# Renders a turnaround preview of character.blend (front / 3-4 / side).
#   blender --background Assets/Models/player6/character.blend --python Tools/blender/render_preview.py -- <out.png>
import math
import sys

import bpy
from mathutils import Vector

out = sys.argv[sys.argv.index("--") + 1]
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE_NEXT"
scene.render.resolution_x, scene.render.resolution_y = 1200, 800
scene.render.film_transparent = False

world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.75, 0.95, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
scene.collection.objects.link(sun)

# three copies of the character side by side, rotated
body = bpy.data.objects["Armature"]
for i, (dx, rz) in enumerate(((-0.9, 0), (0, 35), (0.9, 90))):
    if i == 0:
        obj = body
    else:
        obj = body.copy()
        obj.data = body.data
        scene.collection.objects.link(obj)
        for child in body.children:
            c = child.copy()
            c.parent = obj
            for m in c.modifiers:
                if m.type == "ARMATURE":
                    m.object = obj
            scene.collection.objects.link(c)
    obj.location.x = dx
    obj.rotation_euler.z = math.radians(rz)

cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2.9
cam.location = (0, -6, 0.95)
cam.rotation_euler = (math.radians(90), 0, 0)
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
