# Builds the Exercise 6 player character in Blender and exports it for Godot.
#
#   blender --background --factory-startup --python Tools/blender/make_character.py -- <project_dir>
#
# The character is a low-poly "chibi ninja" made from primitives. It is rigged
# with a Mixamo-style skeleton (mixamorig:Hips, mixamorig:Spine, ...) in T-pose,
# so Godot can retarget it with "Mixamo BoneMap.tres" from
# Godot4-OpenAnimationLibraries and play MeleeLib / ShooterLib animations.
#
# The face is a separate mesh wrapped on the front of the head that shows
# Assets/Models/player6/face.png. Replace that PNG (e.g. with a cropped photo of
# your own face, transparent outside the face) and re-run the script.
#
# Outputs:
#   Assets/Models/player6/character.glb   (model + skeleton, no animations)
#   Assets/Models/player6/character.blend (editable source)
#   Assets/Models/player6/face.png        (only generated if missing)

import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PROJECT = os.path.abspath(argv[0] if argv else os.getcwd())
PREFIX = argv[1] if len(argv) > 1 else "mixamorig:"
OUT_DIR = os.path.join(PROJECT, "Assets", "Models", "player6")
os.makedirs(OUT_DIR, exist_ok=True)
FACE_PNG = os.path.join(OUT_DIR, "face.png")

# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- skeleton
# Character faces -Y (Mixamo / glTF front). Character's left side is +X.
# name: (head, tail, parent)
BONES = {
    "Hips": ((0, 0, 0.92), (0, 0, 1.02), None),
    "Spine": ((0, 0, 1.02), (0, 0, 1.12), "Hips"),
    "Spine1": ((0, 0, 1.12), (0, 0, 1.23), "Spine"),
    "Spine2": ((0, 0, 1.23), (0, 0, 1.36), "Spine1"),
    "Neck": ((0, 0, 1.36), (0, 0, 1.44), "Spine2"),
    "Head": ((0, 0, 1.44), (0, 0, 1.78), "Neck"),
    "HeadTop_End": ((0, 0, 1.78), (0, 0, 1.90), "Head"),
}
for side, s in (("Left", 1), ("Right", -1)):
    BONES.update({
        f"{side}Shoulder": ((0.05 * s, 0, 1.32), (0.17 * s, 0, 1.32), "Spine2"),
        f"{side}Arm": ((0.17 * s, 0, 1.32), (0.42 * s, 0, 1.32), f"{side}Shoulder"),
        f"{side}ForeArm": ((0.42 * s, 0, 1.32), (0.64 * s, 0, 1.32), f"{side}Arm"),
        f"{side}Hand": ((0.64 * s, 0, 1.32), (0.74 * s, 0, 1.32), f"{side}ForeArm"),
        f"{side}UpLeg": ((0.10 * s, 0, 0.90), (0.10 * s, 0, 0.50), "Hips"),
        f"{side}Leg": ((0.10 * s, 0, 0.50), (0.10 * s, 0, 0.10), f"{side}UpLeg"),
        f"{side}Foot": ((0.10 * s, 0, 0.10), (0.10 * s, -0.12, 0.03), f"{side}Leg"),
        f"{side}ToeBase": ((0.10 * s, -0.12, 0.03), (0.10 * s, -0.20, 0.03), f"{side}Foot"),
        f"{side}Toe_End": ((0.10 * s, -0.20, 0.03), (0.10 * s, -0.25, 0.03), f"{side}ToeBase"),
    })

arm_data = bpy.data.armatures.new("Armature")
arm_obj = bpy.data.objects.new("Armature", arm_data)
scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode="EDIT")
for name, (head, tail, parent) in BONES.items():
    b = arm_data.edit_bones.new(PREFIX + name)
    b.head, b.tail = Vector(head), Vector(tail)
    b.roll = 0.0
    if parent:
        b.parent = arm_data.edit_bones[PREFIX + parent]
        b.use_connect = (Vector(head) - arm_data.edit_bones[PREFIX + parent].tail).length < 1e-4
bpy.ops.object.mode_set(mode="OBJECT")

# ---------------------------------------------------------------- materials
def make_mat(name, rgb, rough=0.8):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    return m

def srgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

MAT = {
    "skin": make_mat("Skin", srgb("c98558")),
    "hair": make_mat("Hair", srgb("2b1d16")),
    "suit": make_mat("Suit", srgb("2f3a56")),
    "belt": make_mat("Belt", srgb("d8a13a"), 0.5),
    "band": make_mat("Headband", srgb("b02a24")),
    "boot": make_mat("Boot", srgb("1d1f26")),
    "glove": make_mat("Glove", srgb("3d4a6b")),
}

# ---------------------------------------------------------------- face texture
def default_face(path, size=512):
    """Draws a simple cartoon face with transparent background."""
    y, x = np.mgrid[0:size, 0:size] / size  # y: 0 = bottom (Blender image rows)
    img = np.zeros((size, size, 4), np.float32)

    def paint(mask, rgba):
        img[mask] = rgba

    def ellipse(cx, cy, rx, ry):
        return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0

    for cx in (0.34, 0.66):
        paint(ellipse(cx, 0.52, 0.085, 0.11), (1, 1, 1, 1))              # eye white
        paint(ellipse(cx + 0.01, 0.50, 0.055, 0.075), (0.16, 0.10, 0.06, 1))  # iris
        paint(ellipse(cx + 0.01, 0.50, 0.028, 0.04), (0.02, 0.02, 0.02, 1))   # pupil
        paint(ellipse(cx + 0.03, 0.54, 0.018, 0.022), (1, 1, 1, 1))       # highlight
        brow = ellipse(cx, 0.69, 0.09, 0.022) & ~ellipse(cx, 0.675, 0.09, 0.02)
        paint(brow, (0.17, 0.11, 0.08, 1))
        paint(ellipse(cx + (0.05 if cx > 0.5 else -0.05), 0.36, 0.06, 0.03), (0.95, 0.55, 0.55, 0.55))
    smile = ellipse(0.5, 0.30, 0.11, 0.08) & ~ellipse(0.5, 0.325, 0.11, 0.08) & (y < 0.30)
    paint(smile, (0.45, 0.12, 0.12, 1))

    im = bpy.data.images.new("face_default", size, size, alpha=True)
    im.pixels.foreach_set(img.ravel())
    im.filepath_raw = path
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)

if not os.path.exists(FACE_PNG):
    default_face(FACE_PNG)

face_mat = bpy.data.materials.new("Face")
face_mat.use_nodes = True
nt = face_mat.node_tree
bsdf = nt.nodes["Principled BSDF"]
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(FACE_PNG)
tex.image.pack()
tex.extension = "CLIP"
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
bsdf.inputs["Roughness"].default_value = 0.8
try:
    face_mat.blend_method = "CLIP"
except (AttributeError, TypeError):
    pass

# ---------------------------------------------------------------- body parts
parts = []

def finish(obj, bone, mat, smooth=False):
    obj.data.materials.append(MAT[mat] if isinstance(mat, str) else mat)
    vg = obj.vertex_groups.new(name=PREFIX + bone)
    vg.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    for p in obj.data.polygons:
        p.use_smooth = smooth
    parts.append(obj)
    return obj

def sphere(loc, scale, bone, mat, seg=12, rings=8, smooth=False):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, bone, mat, smooth)

def cyl(a, b, r1, r2, bone, mat, verts=10):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=d.length,
                                    location=(a + b) / 2)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    bpy.ops.object.transform_apply(rotation=True)
    return finish(o, bone, mat)

def box(loc, size, bone, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        mod = o.modifiers.new("Bevel", "BEVEL")
        mod.width, mod.segments = bevel, 2
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return finish(o, bone, mat)

# Head: the sphere radius also drives the face mesh below.
HEAD_C = Vector((0, 0, 1.60))
HEAD_R = Vector((0.20, 0.19, 0.21))
sphere(HEAD_C, HEAD_R, "Head", "skin", 20, 14, smooth=True)
# hair cap (top/back) + headband
hair = sphere(HEAD_C + Vector((0, 0.025, 0.035)), HEAD_R * 1.07, "Head", "hair", 20, 14, smooth=True)
bm_cut = [v.index for v in hair.data.vertices if v.co.z < HEAD_C.z + 0.03 and v.co.y < HEAD_C.y + 0.02]
bpy.context.view_layer.objects.active = hair
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="DESELECT")
bpy.ops.object.mode_set(mode="OBJECT")
for i in bm_cut:
    hair.data.vertices[i].select = True
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.delete(type="VERT")
bpy.ops.object.mode_set(mode="OBJECT")
cyl(HEAD_C + Vector((0, 0, 0.10)), HEAD_C + Vector((0, 0, 0.15)), 0.215, 0.21, "Head", "band", 20)
# headband tails at the back
box(HEAD_C + Vector((0.04, 0.24, 0.08)), (0.05, 0.10, 0.025), "Head", "band")
box(HEAD_C + Vector((-0.04, 0.25, 0.06)), (0.05, 0.12, 0.025), "Head", "band")
# ears
for s in (1, -1):
    sphere(HEAD_C + Vector((0.20 * s, 0.01, -0.01)), (0.03, 0.04, 0.05), "Head", "skin", 8, 6)

# Face: a grid wrapped onto the front of the head ellipsoid, UV = grid coords.
FW, FH, FN = 0.30, 0.30, 16
bpy.ops.mesh.primitive_grid_add(x_subdivisions=FN, y_subdivisions=FN, size=1, calc_uvs=True)
face = bpy.context.object
face.name = "Face"
for v in face.data.vertices:
    fx, fz = v.co.x * FW, v.co.y * FH  # grid is in XY, map its Y to height
    nx, nz = fx / HEAD_R.x, fz / HEAD_R.z
    ny = math.sqrt(max(0.0, 1.0 - nx * nx - nz * nz))
    v.co = HEAD_C + Vector((fx, -(ny * HEAD_R.y + 0.004), fz - 0.02))
# grid normals must point forward (-Y)
bpy.context.view_layer.objects.active = face
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")
if sum(p.normal.y for p in face.data.polygons) > 0:
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode="OBJECT")
finish(face, "Head", face_mat, smooth=True)

# Neck & torso
cyl((0, 0, 1.33), (0, 0, 1.45), 0.06, 0.055, "Neck", "skin")
cyl((0, 0, 1.12), (0, 0, 1.37), 0.17, 0.20, "Spine2", "suit", 12)       # chest
sphere((0, 0, 1.36), (0.20, 0.14, 0.05), "Spine2", "suit", 12, 6)       # shoulder top
cyl((0, 0, 1.00), (0, 0, 1.13), 0.16, 0.17, "Spine", "suit", 12)        # belly
cyl((0, 0, 1.00), (0, 0, 1.06), 0.175, 0.175, "Spine", "belt", 12)      # belt
box((0, -0.17, 1.03), (0.07, 0.03, 0.07), "Spine", "belt")               # buckle
cyl((0, 0, 0.84), (0, 0, 1.01), 0.17, 0.165, "Hips", "suit", 12)        # pelvis
# scarf around the neck
cyl((0, 0, 1.36), (0, 0, 1.41), 0.12, 0.09, "Spine2", "band", 12)

for side, s in (("Left", 1), ("Right", -1)):
    sphere((0.18 * s, 0, 1.32), (0.075, 0.075, 0.075), f"{side}Arm", "suit", 10, 6)
    cyl((0.18 * s, 0, 1.32), (0.43 * s, 0, 1.32), 0.06, 0.05, f"{side}Arm", "suit")
    sphere((0.43 * s, 0, 1.32), (0.05, 0.05, 0.05), f"{side}ForeArm", "glove", 8, 6)
    cyl((0.43 * s, 0, 1.32), (0.64 * s, 0, 1.32), 0.05, 0.045, f"{side}ForeArm", "glove")
    sphere((0.69 * s, -0.01, 1.32), (0.065, 0.045, 0.055), f"{side}Hand", "skin", 10, 6, smooth=True)
    sphere((0.66 * s, -0.05, 1.33), (0.02, 0.03, 0.02), f"{side}Hand", "skin", 6, 4)  # thumb

    sphere((0.10 * s, 0, 0.86), (0.09, 0.09, 0.09), f"{side}UpLeg", "suit", 10, 6)
    cyl((0.10 * s, 0, 0.88), (0.10 * s, 0, 0.50), 0.085, 0.07, f"{side}UpLeg", "suit")
    sphere((0.10 * s, 0, 0.50), (0.068, 0.068, 0.068), f"{side}Leg", "suit", 10, 6)
    cyl((0.10 * s, 0, 0.50), (0.10 * s, 0, 0.12), 0.068, 0.06, f"{side}Leg", "boot")
    box((0.10 * s, -0.04, 0.065), (0.12, 0.25, 0.13), f"{side}Foot", "boot", bevel=0.025)

# ---------------------------------------------------------------- join & skin
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
body = bpy.context.object
body.name = "Body"
body.data.name = "BodyMesh"
body.parent = arm_obj
mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm_obj

# ---------------------------------------------------------------- save/export
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "character.blend"))
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT_DIR, "character.glb"),
    export_format="GLB",
    export_animations=False,
    export_skins=True,
    export_yup=True,
)
print("EXPORTED", os.path.join(OUT_DIR, "character.glb"), "prefix", PREFIX)
