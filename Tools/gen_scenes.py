"""Generates the Sky Ninja scenes. Run from the project root:  python Tools/gen_scenes.py

After generating, the scenes are normal Godot scenes and can be edited in the editor
(re-running this script overwrites them)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from tscn import Scene, q, vec3, color, xf  # noqa: E402

M = "res://Assets/Models/"
S = "res://Scripts/"
G = "res://Scenes/Gameplay/"
W = "res://Scenes/World/"

os.makedirs("Scenes/Gameplay", exist_ok=True)
os.makedirs("Scenes/World", exist_ok=True)
os.makedirs("Scenes/Levels", exist_ok=True)
os.makedirs("Scenes/UI", exist_ok=True)


def mat(s, col, emission=0.0, rough=0.85, extra=None):
    props = dict(albedo_color=color(*col), roughness=rough)
    if emission:
        props.update(emission_enabled=True, emission=color(*col), emission_energy_multiplier=emission)
    if extra:
        props.update(extra)
    return s.sub("StandardMaterial3D", **props)


# --------------------------------------------------------------------------- PLAYER
def player():
    s = Scene("Player", "CharacterBody3D", script=S + "player.gd", groups=["Player"], jump_force=6.0)
    cap = s.sub("CapsuleShape3D", radius=0.4, height=1.36)
    s.node("CollisionShape3D", "CollisionShape3D", transform=xf((0, 0.68, 0)), shape=cap)
    s.node("Model", "Node3D")
    s.node("FlipPivot", "Node3D", "Model", transform=xf((0, 0.65, 0)))
    s.node("character", None, "Model/FlipPivot", instance=M + "player6/character.glb", transform=xf((0, -0.65, 0), scale=0.72))
    s.node("AnimationPlayer", "AnimationPlayer", "Model", root_node='NodePath("../FlipPivot/character")',
           libraries='{\n&"": ' + s.res(M + "player6/player6_animations.res", "AnimationLibrary") + "\n}",
           autoplay=q("Idle"))
    s.node("Gimbal", "Node3D", unique_name_in_owner=True, transform=xf((0, 1, 0)), script=s.res(S + "CameraMovement.gd"))
    s.node("Camera3D", "Camera3D", "Gimbal", transform=xf((0, 2, 5), (-15, 0, 0)), current=True, fov=70.0)
    pmat = s.sub("StandardMaterial3D", diffuse_mode=2, specular_mode=2, metallic_specular=0.0)
    curve = s.sub("Curve", _data="[Vector2(0, 0), 0.0, 0.0, 0, 0, Vector2(0.236318, 1), 0.0, 0.0, 0, 0, Vector2(1, 0), 0.0, 0.0, 0, 0]", point_count=3)
    s.node("ParticleTrail", "CPUParticles3D", material_override=pmat, amount=30,
           mesh=s.res("res://Assets/Resources/cloud.res", "ArrayMesh"), emission_shape=1, emission_sphere_radius=0.2,
           particle_flag_align_y=True, direction=vec3(0, 0, 0), gravity=vec3(0, 0.1, 0), scale_amount_min=0.75,
           scale_amount_curve=curve)
    s.node("Footsteps", "AudioStreamPlayer3D", stream=s.res("res://Assets/Audio/SFX/walking.ogg"), pitch_scale=0.75, autoplay=True)
    s.write("Scenes/player.tscn")


# --------------------------------------------------------------------------- GAMEPLAY OBJECTS
def hazard_area(s, parent, shape, transform=None):
    props = dict(script=s.res(S + "Gameplay/Hazard.gd"))
    s.node("Hazard", "Area3D", parent, **props)
    p = "Hazard" if parent == "." else parent + "/Hazard"
    cprops = dict(shape=shape)
    if transform:
        cprops["transform"] = transform
    s.node("CollisionShape3D", "CollisionShape3D", p, **cprops)


def saw_blade():
    s = Scene("SawBlade", "Node3D", script=S + "Gameplay/Mover.gd")
    s.node("Spin", "Node3D", script=s.res(S + "Gameplay/Mover.gd"), spin_degrees=vec3(0, 0, -400))
    s.node("Model", None, "Spin", instance=M + "props/saw_blade.glb")
    hazard_area(s, "Spin", s.sub("CylinderShape3D", radius=1.3, height=0.35), xf(rot=(90, 0, 0)))
    s.write("Scenes/Gameplay/SawBlade.tscn")


def spiky_ball():
    s = Scene("SpikyBall", "Node3D", script=S + "Gameplay/Mover.gd", spin_degrees=vec3(0, 90, 0))
    metal = mat(s, (0.25, 0.25, 0.3), rough=0.4, extra=dict(metallic=0.6))
    s.node("Post", "MeshInstance3D", transform=xf((0, 0.5, 0)),
           mesh=s.sub("CylinderMesh", top_radius=0.12, bottom_radius=0.25, height=1.0, radial_segments=8, material=metal))
    s.node("Arm", "MeshInstance3D", transform=xf((1.5, 0.75, 0)),
           mesh=s.sub("BoxMesh", size=vec3(3, 0.08, 0.08), material=metal))
    s.node("Ball", "Node3D", transform=xf((3, 0.75, 0)))
    s.node("Model", None, "Ball", instance=M + "props/spiky_ball.glb", transform=xf(scale=1.1))
    hazard_area(s, "Ball", s.sub("SphereShape3D", radius=0.6))
    s.write("Scenes/Gameplay/SpikyBall.tscn")


def spin_bar():
    s = Scene("SpinBar", "Node3D", script=S + "Gameplay/Mover.gd", spin_degrees=vec3(0, 75, 0))
    s.node("BarA", None, instance=M + "props/cylinder_hazard.glb", transform=xf((0.35, 0.45, 0), (0, 0, -90), (0.28, 1.0, 0.28)))
    s.node("BarB", None, instance=M + "props/cylinder_hazard.glb", transform=xf((-0.35, 0.45, 0), (0, 0, 90), (0.28, 1.0, 0.28)))
    metal = mat(s, (0.95, 0.75, 0.2), rough=0.4)
    s.node("Hub", "MeshInstance3D", transform=xf((0, 0.5, 0)),
           mesh=s.sub("CylinderMesh", top_radius=0.35, bottom_radius=0.45, height=1.0, radial_segments=8, material=metal))
    hazard_area(s, ".", s.sub("BoxShape3D", size=vec3(8.4, 0.55, 0.6)), xf((0, 0.45, 0)))
    s.write("Scenes/Gameplay/SpinBar.tscn")


def spike_trap():
    s = Scene("SpikeTrap", "Node3D", script=S + "Gameplay/SpikeTrap.gd")
    s.node("Model", None, instance=M + "props/spike_trap.glb")
    hazard_area(s, ".", s.sub("BoxShape3D", size=vec3(1.7, 1.0, 1.7)), xf((0, 0.5, 0)))
    s.node("Warning", "MeshInstance3D", transform=xf((0, 0.03, 0)), visible=False,
           mesh=s.sub("BoxMesh", size=vec3(2.05, 0.04, 2.05), material=mat(s, (1, 0.15, 0.1), emission=2.0)))
    s.write("Scenes/Gameplay/SpikeTrap.tscn")


def spikes():
    s = Scene("Spikes", "Node3D")
    s.node("Model", None, instance=M + "props/spikes.glb", transform=xf(scale=0.4))
    hazard_area(s, ".", s.sub("BoxShape3D", size=vec3(0.7, 1.2, 0.7)), xf((0, 0.6, 0)))
    s.write("Scenes/Gameplay/Spikes.tscn")


def bouncer():
    s = Scene("Bouncer", "Area3D", script=S + "Gameplay/Bouncer.gd")
    s.node("Model", None, instance=M + "props/spring.glb", transform=xf(scale=0.7))
    s.node("CollisionShape3D", "CollisionShape3D", transform=xf((0, 1.0, 0)), shape=s.sub("CylinderShape3D", radius=0.75, height=0.8))
    s.write("Scenes/Gameplay/Bouncer.tscn")


def moving_platform():
    s = Scene("MovingPlatform", "AnimatableBody3D", script=S + "Gameplay/Mover.gd")
    top = mat(s, (0.97, 0.97, 1.0), rough=1.0, extra=dict(rim_enabled=True, rim=0.5))
    s.node("Top", "MeshInstance3D", transform=xf((0, -0.25, 0)),
           mesh=s.sub("CylinderMesh", top_radius=1.7, bottom_radius=1.3, height=0.5, radial_segments=9, rings=0, material=top))
    s.node("Cloud", "Node3D", script=s.res(S + "World/CloudPuff.gd"), transform=xf((0, -0.55, 0)), size=1.2, variation=3, drift=0.0)
    s.node("CollisionShape3D", "CollisionShape3D", transform=xf((0, -0.25, 0)), shape=s.sub("CylinderShape3D", radius=1.6, height=0.5))
    s.write("Scenes/Gameplay/MovingPlatform.tscn")


def checkpoint():
    s = Scene("Checkpoint", "Area3D", script=S + "Gameplay/Checkpoint.gd")
    s.node("Flag", None, instance=M + "props/goal_flag.glb", transform=xf(scale=0.8))
    s.node("CollisionShape3D", "CollisionShape3D", transform=xf((0, 1.25, 0)), shape=s.sub("BoxShape3D", size=vec3(2, 2.5, 2)))
    s.write("Scenes/Gameplay/Checkpoint.tscn")


def door():
    s = Scene("Door", "Node3D", script=S + "Gameplay/Door.gd")
    stone = mat(s, (0.93, 0.9, 0.84))
    trim = mat(s, (0.95, 0.72, 0.2), rough=0.5)
    wood = mat(s, (0.55, 0.33, 0.2))
    for side in (-1, 1):
        s.node("Pillar" + ("L" if side < 0 else "R"), "MeshInstance3D", transform=xf((1.55 * side, 1.9, 0)),
               mesh=s.sub("BoxMesh", size=vec3(0.7, 3.8, 0.8), material=stone))
    s.node("Beam", "MeshInstance3D", transform=xf((0, 4.05, 0)), mesh=s.sub("BoxMesh", size=vec3(4.4, 0.55, 1.0), material=trim))
    s.node("Roof", "MeshInstance3D", transform=xf((0, 4.5, 0)),
           mesh=s.sub("PrismMesh", size=vec3(4.9, 0.6, 1.2), material=stone))
    s.node("Frame", "StaticBody3D")
    for i, (pos, size) in enumerate([((-1.55, 1.9, 0), (0.7, 3.8, 0.8)), ((1.55, 1.9, 0), (0.7, 3.8, 0.8)), ((0, 4.2, 0), (4.4, 0.9, 1.0))]):
        s.node(f"Shape{i}", "CollisionShape3D", "Frame", transform=xf(pos), shape=s.sub("BoxShape3D", size=vec3(*size)))
    s.node("Blocker", "StaticBody3D")
    s.node("CollisionShape3D", "CollisionShape3D", "Blocker", transform=xf((0, 1.6, 0)), shape=s.sub("BoxShape3D", size=vec3(2.4, 3.2, 0.3)))
    leaf = s.sub("BoxMesh", size=vec3(1.2, 3.2, 0.15), material=wood)
    knob = s.sub("SphereMesh", radius=0.08, height=0.16, material=trim)
    s.node("LeftHinge", "Node3D", transform=xf((-1.2, 0, 0)))
    s.node("Leaf", "MeshInstance3D", "LeftHinge", transform=xf((0.6, 1.6, 0)), mesh=leaf)
    s.node("Knob", "MeshInstance3D", "LeftHinge", transform=xf((1.0, 1.5, 0.12)), mesh=knob)
    s.node("RightHinge", "Node3D", transform=xf((1.2, 0, 0)))
    s.node("Leaf", "MeshInstance3D", "RightHinge", transform=xf((-0.6, 1.6, 0)), mesh=leaf)
    s.node("Knob", "MeshInstance3D", "RightHinge", transform=xf((-1.0, 1.5, 0.12)), mesh=knob)
    shader = s.sub("Shader", code=q("""shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled;
uniform vec4 color_a : source_color = vec4(0.2, 0.75, 1.0, 1.0);
uniform vec4 color_b : source_color = vec4(1.0, 1.0, 1.0, 1.0);
void fragment() {
	vec2 uv = UV * 2.0 - 1.0;
	float r = length(uv);
	float a = atan(uv.y, uv.x);
	float swirl = sin(a * 4.0 + r * 9.0 - TIME * 5.0) * 0.5 + 0.5;
	ALBEDO = mix(color_a.rgb, color_b.rgb, swirl * (1.0 - r) + (1.0 - r) * 0.4);
	ALPHA = smoothstep(1.0, 0.85, r) * (0.7 + 0.3 * swirl);
}"""))
    s.node("Portal", "MeshInstance3D", transform=xf((0, 1.6, -0.05)),
           mesh=s.sub("QuadMesh", size="Vector2(2.4, 3.2)", material=s.sub("ShaderMaterial", shader=shader)))
    s.node("Lock", "Node3D", transform=xf((0, 1.9, 0.45)))
    s.node("Body", "MeshInstance3D", "Lock", mesh=s.sub("BoxMesh", size=vec3(0.6, 0.5, 0.2), material=trim))
    s.node("Shackle", "MeshInstance3D", "Lock", transform=xf((0, 0.3, 0), (90, 0, 0)),
           mesh=s.sub("TorusMesh", inner_radius=0.14, outer_radius=0.22, rings=12, ring_segments=6, material=trim))
    s.node("Light", "OmniLight3D", transform=xf((0, 1.8, 1.0)), light_color=color(0.4, 0.85, 1), light_energy=3.0, omni_range=7.0)
    pm = s.sub("StandardMaterial3D", transparency=1, shading_mode=0, vertex_color_use_as_albedo=True,
               albedo_texture=s.res("res://Assets/Textures/particle.png"), billboard_mode=3,
               particles_anim_h_frames=1, particles_anim_v_frames=1)
    grad = s.sub("Gradient", colors="PackedColorArray(0.6, 0.95, 1, 1, 1, 1, 1, 0)")
    s.node("Sparkles", "CPUParticles3D", transform=xf((0, 1.6, 0.3)), amount=24, lifetime=1.6,
           mesh=s.sub("QuadMesh", material=pm, size="Vector2(0.25, 0.25)"), emission_shape=3,
           emission_box_extents=vec3(1.1, 1.5, 0.2), direction=vec3(0, 1, 0), spread=30.0, gravity=vec3(0, 0.5, 0),
           initial_velocity_min=0.2, initial_velocity_max=0.8, color_ramp=grad)
    s.node("Sign", "Label3D", transform=xf((0, 4.05, 0.52)), text=q("GOAL"), font_size=96, outline_size=18,
           modulate=color(0.45, 0.25, 0.05), outline_modulate=color(1, 0.95, 0.7))
    s.node("Trigger", "Area3D")
    s.node("CollisionShape3D", "CollisionShape3D", "Trigger", transform=xf((0, 1.5, 0.2)), shape=s.sub("BoxShape3D", size=vec3(2.3, 3.0, 1.4)))
    s.write("Scenes/Gameplay/Door.tscn")


def lantern():
    s = Scene("Lantern", "Node3D")
    wood = mat(s, (0.35, 0.22, 0.15))
    s.node("Post", "MeshInstance3D", transform=xf((0, 0.9, 0)),
           mesh=s.sub("CylinderMesh", top_radius=0.07, bottom_radius=0.1, height=1.8, radial_segments=6, material=wood))
    s.node("Lamp", "MeshInstance3D", transform=xf((0, 1.95, 0)),
           mesh=s.sub("SphereMesh", radius=0.22, height=0.44, radial_segments=8, rings=4, material=mat(s, (1, 0.7, 0.3), emission=3.0)))
    s.node("Cap", "MeshInstance3D", transform=xf((0, 2.22, 0)),
           mesh=s.sub("CylinderMesh", top_radius=0.0, bottom_radius=0.3, height=0.2, radial_segments=6, material=wood))
    s.node("Light", "OmniLight3D", transform=xf((0, 2.0, 0)), light_color=color(1, 0.7, 0.4), light_energy=2.0, omni_range=6.0)
    s.write("Scenes/World/Lantern.tscn")


# --------------------------------------------------------------------------- UI
def theme():
    def box(bg, border, radius=16, bottom=6, draw=True, width=0):
        lines = [f"bg_color = {color(*bg)}", f"draw_center = {'true' if draw else 'false'}",
                 f"border_width_left = {width}", f"border_width_top = {width}", f"border_width_right = {width}",
                 f"border_width_bottom = {bottom}", f"border_color = {color(*border)}"]
        lines += [f"corner_radius_{c} = {radius}" for c in ("top_left", "top_right", "bottom_right", "bottom_left")]
        lines += [f"content_margin_{c} = {m}" for c, m in (("left", 24), ("top", 10), ("right", 24), ("bottom", 14))]
        return "\n".join(lines)

    styles = {
        "normal": box((1, 0.78, 0.26), (0.78, 0.47, 0.13)),
        "hover": box((1, 0.86, 0.42), (0.78, 0.47, 0.13)),
        "pressed": box((0.93, 0.65, 0.2), (0.6, 0.35, 0.1), bottom=2),
        "focus": box((0, 0, 0, 0), (1, 1, 1), draw=False, width=4, bottom=4),
        "panel": box((0.1, 0.14, 0.3, 0.85), (0.4, 0.7, 1.0), radius=24, width=3, bottom=3),
    }
    out = [f"[gd_resource type=\"Theme\" load_steps={len(styles) + 1} format=3]", ""]
    for name, body in styles.items():
        out += [f'[sub_resource type="StyleBoxFlat" id="{name}"]', body, ""]
    out += ["[resource]", "default_font_size = 26",
            f"Button/colors/font_color = {color(0.3, 0.16, 0.05)}",
            f"Button/colors/font_hover_color = {color(0.3, 0.16, 0.05)}",
            f"Button/colors/font_pressed_color = {color(0.3, 0.16, 0.05)}",
            f"Button/colors/font_focus_color = {color(0.3, 0.16, 0.05)}",
            "Button/font_sizes/font_size = 30",
            'Button/styles/normal = SubResource("normal")', 'Button/styles/hover = SubResource("hover")',
            'Button/styles/pressed = SubResource("pressed")', 'Button/styles/focus = SubResource("focus")',
            'PanelContainer/styles/panel = SubResource("panel")',
            f"Label/colors/font_outline_color = {color(0.08, 0.1, 0.25, 0.9)}",
            "Label/constants/outline_size = 10"]
    with open("Assets/Resources/ui_theme.tres", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def full_rect(**extra):
    d = dict(layout_mode=3, anchors_preset=15, anchor_right=1.0, anchor_bottom=1.0, grow_horizontal=2, grow_vertical=2)
    d.update(extra)
    return d


def game_ui():
    s = Scene("GameUI", "CanvasLayer", script=S + "GameUI.gd")
    s.node("HUD", "Control", **full_rect(mouse_filter=2))
    s.node("CoinTexture", "TextureRect", "HUD", layout_mode=0, offset_left=24.0, offset_top=20.0, offset_right=96.0,
           offset_bottom=92.0, texture=s.res("res://Assets/Textures/coin.png"), expand_mode=1, stretch_mode=5)
    s.node("CoinsLabel", "Label", "HUD", layout_mode=0, offset_left=106.0, offset_top=26.0, offset_right=330.0, offset_bottom=90.0,
           theme_override_colors_font_color=color(1, 0.8, 0.3), theme_override_font_sizes_font_size=48, text=q("0 / 0"))
    s.node("StatsLabel", "Label", "HUD", layout_mode=1, anchors_preset=1, anchor_left=1.0, anchor_right=1.0,
           offset_left=-460.0, offset_top=30.0, offset_right=-28.0, offset_bottom=70.0, grow_horizontal=0,
           horizontal_alignment=2, text=q("Time 00:00   Falls 0"))
    s.node("LevelLabel", "Label", "HUD", layout_mode=1, anchors_preset=10, anchor_right=1.0, offset_top=110.0,
           offset_bottom=190.0, grow_horizontal=2, horizontal_alignment=1, theme_override_font_sizes_font_size=64,
           theme_override_constants_outline_size=18, text=q("Level"))
    s.node("HintLabel", "Label", "HUD", layout_mode=1, anchors_preset=12, anchor_top=1.0, anchor_right=1.0,
           anchor_bottom=1.0, offset_top=-170.0, offset_bottom=-100.0, grow_horizontal=2, grow_vertical=0,
           horizontal_alignment=1, theme_override_font_sizes_font_size=36, text=q(""))
    s.node("PauseMenu", "Control", **full_rect())
    s.node("Dim", "ColorRect", "PauseMenu", **full_rect(color=color(0.02, 0.03, 0.1, 0.55)))
    s.node("Center", "CenterContainer", "PauseMenu", **full_rect())
    s.node("Box", "PanelContainer", "PauseMenu/Center", layout_mode=2)
    s.node("VBox", "VBoxContainer", "PauseMenu/Center/Box", layout_mode=2, custom_minimum_size="Vector2(360, 0)",
           theme_override_constants_separation=16)
    s.node("Title", "Label", "PauseMenu/Center/Box/VBox", layout_mode=2, horizontal_alignment=1,
           theme_override_font_sizes_font_size=56, text=q("PAUSED"))
    for name, label in (("Resume", "Resume"), ("Restart", "Restart Level")):
        s.node(name, "Button", "PauseMenu/Center/Box/VBox", layout_mode=2, custom_minimum_size="Vector2(0, 64)", text=q(label))
    s.write("Scenes/UI/game_ui.tscn")


def sky_env(s, top, horizon, bottom, energy=1.0, fog=0.003, glow=True):
    sky_mat = s.sub("ProceduralSkyMaterial", sky_top_color=color(*top), sky_horizon_color=color(*horizon),
                    sky_curve=0.12, ground_bottom_color=color(*bottom), ground_horizon_color=color(*horizon),
                    ground_curve=0.05, sun_angle_max=20.0, sky_energy_multiplier=energy)
    sky = s.sub("Sky", sky_material=sky_mat)
    env = s.sub("Environment", background_mode=2, sky=sky, ambient_light_source=3, ambient_light_sky_contribution=1.0,
                ambient_light_energy=0.5, tonemap_mode=3, tonemap_exposure=1.0, glow_enabled=glow, glow_intensity=0.25,
                fog_enabled=True, fog_light_color=color(*horizon), fog_density=fog, fog_sky_affect=0.0,
                adjustment_enabled=True, adjustment_saturation=1.2, adjustment_contrast=1.05)
    s.node("WorldEnvironment", "WorldEnvironment", environment=env)


def island(s, name, pos, radius, depth=5.0, sides=8, variation=0, parent="Islands", **colors):
    props = dict(transform=xf(pos, (0, variation * 17 % 45, 0)), script=s.res(S + "World/Island.gd"),
                 radius=float(radius), depth=float(depth), sides=sides, variation=variation)
    for k, v in colors.items():
        props[k] = color(*v)
    s.node(name, "StaticBody3D", parent, **props)


def tree(s, name, pos, kind=1, height=3.0, variation=0, parent="Decor", leaf=None, trunk=None):
    props = dict(transform=xf(pos, (0, variation * 37, 0)), script=s.res(S + "World/LowPolyTree.gd"),
                 kind=kind, height=float(height), variation=variation)
    if leaf:
        props["leaf_color"] = color(*leaf)
    if trunk:
        props["trunk_color"] = color(*trunk)
    s.node(name, "StaticBody3D", parent, **props)


def cloud(s, name, pos, size, variation, parent="Clouds", col=None):
    props = dict(transform=xf(pos), script=s.res(S + "World/CloudPuff.gd"), size=float(size), variation=variation)
    if col:
        props["color"] = color(*col)
    s.node(name, "Node3D", parent, **props)


def part(s, name, glb, part_name, pos, rot_y=0, scale=1.0, parent="Decor"):
    s.node(name, None, parent, instance=M + glb, transform=xf(pos, (0, rot_y, 0), scale),
           script=s.res(S + "World/ModelPart.gd"), part=q(part_name))


def prop(s, name, glb, pos, rot_y=0, scale=1.0, parent="Decor"):
    s.node(name, None, parent, instance=M + glb, transform=xf(pos, (0, rot_y, 0), scale))


def coin(s, i, pos):
    s.node(f"Coin{i}", None, "Coins", instance="res://Scenes/Coin.tscn", transform=xf(pos))


def menu_scene(path, script, title, subtitle, buttons, stats=False, tint=((0.3, 0.6, 1), (0.85, 0.93, 1), (0.6, 0.8, 1))):
    s = Scene("Menu", "Node3D", script=script)
    sky_env(s, *tint, fog=0.01)
    s.node("Sun", "DirectionalLight3D", transform=xf((0, 10, 0), (-50, -30, 0)), shadow_enabled=True, light_energy=1.1)
    s.node("Islands", "Node3D")
    island(s, "Home", (0, 0, 0), 4.0, depth=4.0, variation=2)
    island(s, "Far1", (-9, -2, -7), 2.5, depth=3.0, variation=5)
    island(s, "Far2", (10, 1, -9), 3.0, depth=3.5, variation=8)
    s.node("Decor", "Node3D")
    tree(s, "Tree1", (-2.3, 0, -1.6), 1, 2.8, 1)
    tree(s, "Tree2", (2.4, 0, -1.2), 0, 3.2, 2)
    tree(s, "Tree3", (-9, -2, -7), 0, 2.6, 4)
    tree(s, "Tree4", (10, 1, -9), 1, 3.0, 6)
    part(s, "Bush", "nature/bushes.glb", "Bush_Flowers", (1.6, 0, 1.6), 30, 0.8)
    part(s, "Flowers", "nature/flowers.glb", "Flower_3_Clump", (-1.4, 0, 1.8), 0, 1.0)
    prop(s, "Crate", "props/crate.glb", (-2.6, 0.35, 1.0), 20, 0.35)
    s.node("Ninja", None, instance=M + "player6/character.glb", transform=xf((0, 0, 0.3), scale=0.72))
    s.node("AnimationPlayer", "AnimationPlayer", "Ninja", root_node='NodePath("..")',
           libraries='{\n&"": ' + s.res(M + "player6/player6_animations.res", "AnimationLibrary") + "\n}")
    s.node("Clouds", "Node3D")
    for i, (p, sz) in enumerate([((-6, -5, 4), 3), ((7, -6, 2), 4), ((0, -8, -12), 6), ((-14, 3, -16), 4), ((15, 5, -18), 5)]):
        cloud(s, f"Cloud{i}", p, sz, i + 1)
    s.node("CameraPivot", "Node3D", transform=xf((0, 0.75, 0)))
    s.node("Camera3D", "Camera3D", "CameraPivot", transform=xf((0, 0.9, 4.6), (-10, 0, 0)), current=True, fov=60.0)
    s.node("UI", "CanvasLayer")
    s.node("Title", "Label", "UI", layout_mode=1, anchors_preset=10, anchor_right=1.0, offset_top=40.0, offset_bottom=170.0,
           grow_horizontal=2, horizontal_alignment=1, theme_override_colors_font_color=color(1, 0.84, 0.3),
           theme_override_constants_outline_size=28, theme_override_font_sizes_font_size=110, text=q(title))
    s.node("Subtitle", "Label", "UI", layout_mode=1, anchors_preset=10, anchor_right=1.0, offset_top=165.0,
           offset_bottom=215.0, grow_horizontal=2, horizontal_alignment=1, theme_override_font_sizes_font_size=30, text=q(subtitle))
    s.node("Center", "Control", "UI", **full_rect(mouse_filter=2))
    s.node("VBox", "VBoxContainer", "UI/Center", layout_mode=1, anchors_preset=3, anchor_left=1.0, anchor_top=1.0,
           anchor_right=1.0, anchor_bottom=1.0, offset_left=-400.0, offset_top=-340.0 if stats else -220.0,
           offset_right=-60.0, offset_bottom=-60.0, grow_horizontal=0, grow_vertical=0, alignment=2,
           theme_override_constants_separation=16)
    if stats:
        s.node("Stats", "Label", "UI/Center/VBox", layout_mode=2, horizontal_alignment=2,
               theme_override_font_sizes_font_size=36, text=q(""))
    for name, label in buttons:
        s.node(name, "Button", "UI/Center/VBox", layout_mode=2, custom_minimum_size="Vector2(0, 68)", text=q(label))
    s.node("Credits", "Label", "UI", layout_mode=1, anchors_preset=2, anchor_top=1.0, anchor_bottom=1.0,
           offset_left=24.0, offset_top=-110.0, offset_right=820.0, offset_bottom=-16.0, grow_vertical=0,
           theme_override_font_sizes_font_size=18, modulate=color(1, 1, 1, 0.9),
           text=q("Based on 3D Platformer Starter Kit (SD Studios)\nModels: Quaternius via Poly Pizza (CC0)\nMade with Godot 4.7"))
    s.write(path)


# --------------------------------------------------------------------------- LEVELS
def level_common(s, player_pos, deadzone_y):
    s.node("Player", None, instance="res://Scenes/player.tscn", transform=xf(player_pos))
    s.node("DeadZone", "Area3D", transform=xf((0, deadzone_y, -40)), script=s.res(S + "DeadZone.gd"))
    s.node("CollisionShape3D", "CollisionShape3D", "DeadZone", shape=s.sub("BoxShape3D", size=vec3(400, 10, 400)))
    s.node("GameUI", None, instance="res://Scenes/UI/game_ui.tscn")


def level_1():
    s = Scene("Level1", "Node3D", script=S + "World/Level.gd", level_name=q("Level 1 - Sunny Sky Isles"))
    sky_env(s, (0.22, 0.52, 0.95), (0.78, 0.9, 1.0), (0.55, 0.75, 0.98), fog=0.004)
    s.node("Sun", "DirectionalLight3D", transform=xf((0, 20, 0), (-55, -35, 0)), light_color=color(1, 0.96, 0.88),
           light_energy=0.9, shadow_enabled=True, directional_shadow_max_distance=60.0)

    s.node("Islands", "Node3D")
    island(s, "Start", (0, 0, 0), 6.0, depth=6.0, variation=1)
    island(s, "Stone1", (0, 0.3, -9), 1.6, depth=2.5, sides=7, variation=11)
    island(s, "Stone2", (0, 0.6, -13.2), 1.6, depth=2.5, sides=7, variation=12)
    island(s, "TrapIsland", (0, 1.0, -21), 5.0, depth=5.0, variation=2)
    island(s, "SawIsland", (0, 1.5, -38), 5.5, depth=5.5, variation=3)
    island(s, "Stone3", (8.3, 2.0, -38), 1.6, depth=2.5, sides=7, variation=13)
    island(s, "Stone4", (12.2, 2.6, -38), 1.6, depth=2.5, sides=7, variation=14)
    island(s, "GoalIsland", (20, 3.0, -38), 6.5, depth=7.0, variation=4)
    island(s, "Deco1", (-14, -3, -14), 3.0, depth=4.0, variation=21)
    island(s, "Deco2", (16, -1, -12), 2.2, depth=3.0, variation=22)
    island(s, "Deco3", (-12, 4, -46), 2.8, depth=3.5, variation=23)
    island(s, "Deco4", (34, 6, -30), 3.5, depth=4.0, variation=24)

    s.node("Decor", "Node3D")
    tree(s, "Tree1", (-3.6, 0, -0.8), 0, 3.2, 1)
    tree(s, "Tree2", (4.0, 0, 1.6), 1, 3.6, 2)
    tree(s, "Tree3", (-3.8, 0, 3.0), 1, 2.6, 3)
    tree(s, "Tree4", (-3.4, 1.0, -24.2), 0, 2.8, 4)
    tree(s, "Tree5", (-3.5, 1.5, -42.0), 1, 3.0, 5)
    tree(s, "Tree6", (22.5, 3.0, -43.2), 1, 3.8, 6)
    tree(s, "Tree7", (22.5, 3.0, -32.8), 1, 3.4, 7)
    tree(s, "Tree8", (15.5, 3.0, -42.5), 0, 2.6, 8)
    tree(s, "Tree9", (-14, -3, -14), 0, 3.4, 9)
    tree(s, "Tree10", (16, -1, -12), 1, 2.8, 10)
    tree(s, "Tree11", (34, 6, -30), 0, 3.6, 11)
    tree(s, "Tree12", (-12, 4, -46), 1, 3.0, 12)
    part(s, "Bush1", "nature/bushes.glb", "Bush", (-4.2, 0, 1.2), 40, 0.9)
    part(s, "Bush2", "nature/bushes.glb", "Bush_Flowers", (3.2, 0, -3.6), 10, 0.9)
    part(s, "Bush3", "nature/bushes.glb", "Bush_Flowers", (-3.0, 1.0, -17.8), 60, 0.8)
    part(s, "Bush4", "nature/bushes.glb", "Bush", (3.6, 1.5, -41.5), 0, 0.9)
    part(s, "Bush5", "nature/bushes.glb", "Bush_Flowers", (24.8, 3.0, -41.5), 20, 0.9)
    part(s, "Bush6", "nature/bushes.glb", "Bush", (24.8, 3.0, -34.5), 70, 0.9)
    for i, (p, name) in enumerate([((1.6, 0, 3.6), "Flower_3_Clump"), ((-1.8, 0, -3.4), "Flower_4_Clump"),
                                   ((4.6, 0, -1.0), "Flower_1_Clump"), ((2.8, 1.0, -24.6), "Flower_2_Clump"),
                                   ((-1.5, 1.5, -42.2), "Flower_3_Clump"), ((17.0, 3.0, -34.0), "Flower_5_Clump"),
                                   ((17.5, 3.0, -41.8), "Flower_1_Clump"), ((0.8, 0.3, -9.6), "Flower_4_Clump")]):
        part(s, f"Flowers{i}", "nature/flowers.glb", name, p, i * 50, 1.1)
    prop(s, "Rock1", "props/rock.glb", (4.4, 0.1, -2.6), 30, 0.8)
    prop(s, "Rock2", "props/rock.glb", (-4.2, 1.1, -21.5), 120, 0.6)
    prop(s, "Rock3", "props/rock.glb", (4.2, 1.6, -35.0), 200, 0.7)
    prop(s, "Sign1", "props/arrow_sign.glb", (2.2, 0, -4.6), 90, 0.6)
    prop(s, "Sign2", "props/arrow_sign.glb", (3.8, 1.5, -38.6), 0, 0.6)
    prop(s, "Crate1", "props/crate.glb", (-4.6, 0.35, -3.0), 15, 0.35)
    prop(s, "Crate2", "props/crate.glb", (-4.3, 0.35, -2.2), 40, 0.3)
    prop(s, "Plant1", "props/small_plant.glb", (1.2, 1.0, -17.2), 0, 1.0)
    for i in range(3):
        prop(s, f"FenceL{i}", "props/fence.glb", (-5.3, 0, -1.0 + i * 2), 90, 1.0)
        prop(s, f"FenceR{i}", "props/fence.glb", (5.3, 0, -3.0 + i * 2), 90, 1.0)

    s.node("Hazards", "Node3D")
    for i, (x, z, delay) in enumerate([(-2.6, -21, 0.0), (0, -21, 0.9), (2.6, -21, 1.8)]):
        s.node(f"SpikeTrap{i}", None, "Hazards", instance=G + "SpikeTrap.tscn", transform=xf((x, 1.0, z)), start_delay=delay)
    s.node("Saw1", None, "Hazards", instance=G + "SawBlade.tscn", transform=xf((-3.5, 1.9, -36.5)),
           move_offset=vec3(7, 0, 0), move_time=1.8)
    s.node("Saw2", None, "Hazards", instance=G + "SawBlade.tscn", transform=xf((3.5, 1.9, -39.8)),
           move_offset=vec3(-7, 0, 0), move_time=1.8, start_delay=0.9)
    s.node("SpikyBall", None, "Hazards", instance=G + "SpikyBall.tscn", transform=xf((20, 3.0, -38)))
    s.node("Platform1", None, "Hazards", instance=G + "MovingPlatform.tscn", transform=xf((0, 1.2, -27.5)),
           move_offset=vec3(0, 0, -3.5), move_time=2.2)
    s.node("Checkpoint1", None, "Hazards", instance=G + "Checkpoint.tscn", transform=xf((3.4, 1.0, -18.4)))
    s.node("Checkpoint2", None, "Hazards", instance=G + "Checkpoint.tscn", transform=xf((-3.8, 1.5, -34.6)))
    s.node("Door", None, instance=G + "Door.tscn", transform=xf((25.0, 3.0, -38), (0, -90, 0)))

    s.node("Coins", "Node3D")
    for i, p in enumerate([(-2, 0.9, -3.2), (2, 0.9, -3.2), (0, 1.9, -9), (0, 1.5, -13.2), (0, 2.0, -21),
                           (-3.6, 1.9, -19.5), (3.6, 1.9, -23.2), (0, 2.5, -29.2), (0, 2.4, -38.2), (-4.0, 2.4, -38.2),
                           (12.2, 3.6, -38), (18, 4.0, -35.3), (18, 4.0, -40.7)]):
        coin(s, i, p)

    s.node("Clouds", "Node3D")
    rng = [((-10, -9, 4), 7), ((12, -12, -2), 9), ((-6, -14, -30), 11), ((18, -10, -46), 8), ((-20, -6, -40), 6),
           ((30, -8, -18), 7), ((6, -16, -60), 12), ((-28, 8, -70), 9), ((40, 12, -60), 10), ((-30, 14, -10), 8),
           ((0, 18, -90), 14), ((26, -5, 6), 6)]
    for i, (p, sz) in enumerate(rng):
        cloud(s, f"Cloud{i}", p, sz, i + 1)

    level_common(s, (0, 0.2, 2.5), -25)
    s.write("Scenes/Levels/level_1.tscn")


def level_2():
    grass = dict(grass_color=(0.5, 0.72, 0.32), dirt_color=(0.55, 0.3, 0.3), rock_color=(0.45, 0.36, 0.58))
    sakura = (0.98, 0.62, 0.78)
    s = Scene("Level2", "Node3D", script=S + "World/Level.gd", level_name=q("Level 2 - Sunset Sky Fortress"))
    sky_env(s, (0.26, 0.2, 0.5), (1.0, 0.62, 0.45), (0.42, 0.28, 0.52), fog=0.004)
    s.node("Sun", "DirectionalLight3D", transform=xf((0, 20, 0), (-25, 150, 0)), light_color=color(1, 0.72, 0.5),
           light_energy=1.2, shadow_enabled=True, directional_shadow_max_distance=60.0)

    s.node("Islands", "Node3D")
    island(s, "Start", (0, 0, 0), 5.5, depth=6.0, variation=31, **grass)
    island(s, "High", (0, 5.0, -12), 4.5, depth=5.0, variation=32, **grass)
    island(s, "TrapIsland", (0, 7.0, -32), 5.0, depth=5.0, variation=33, **grass)
    island(s, "SawIsland", (0, 7.5, -43.6), 4.5, depth=5.0, variation=34, **grass)
    island(s, "Stone1", (4.0, 8.0, -51), 1.8, depth=2.5, sides=7, variation=35, **grass)
    island(s, "Stone2", (1.0, 8.6, -56), 1.8, depth=2.5, sides=7, variation=36, **grass)
    island(s, "GoalIsland", (0, 9.0, -65), 6.0, depth=7.0, variation=37, **grass)
    island(s, "Deco1", (-15, 2, -20), 3.0, depth=4.0, variation=38, **grass)
    island(s, "Deco2", (14, 10, -40), 2.5, depth=3.0, variation=39, **grass)
    island(s, "Deco3", (-12, 12, -62), 3.5, depth=4.0, variation=40, **grass)

    s.node("Decor", "Node3D")
    for i, (p, kind, h) in enumerate([((-3.4, 0, -1.2), 0, 3.2), ((3.6, 0, 1.4), 0, 2.8), ((-3.2, 5, -13.6), 0, 2.6),
                                      ((3.6, 7, -34.5), 0, 3.0), ((-3.6, 7, -34.5), 1, 3.2), ((-3.6, 9, -62), 0, 3.4),
                                      ((3.8, 9, -62), 0, 3.0), ((-15, 2, -20), 0, 3.6), ((14, 10, -40), 1, 3.0),
                                      ((-12, 12, -62), 0, 3.8)]):
        tree(s, f"Tree{i}", p, kind, h, 40 + i, leaf=sakura if kind == 0 else (0.25, 0.5, 0.42))
    for i, (p, name) in enumerate([((1.8, 0, 3.4), "Flower_2_Clump"), ((-2.0, 0, 3.0), "Flower_3_Clump"),
                                   ((2.8, 7, -29.2), "Flower_1_Clump"), ((-2.5, 9, -60.5), "Flower_4_Clump"),
                                   ((2.5, 9, -60.5), "Flower_5_Clump")]):
        part(s, f"Flowers{i}", "nature/flowers.glb", name, p, i * 70, 1.1)
    part(s, "Bush1", "nature/bushes.glb", "Bush_Flowers", (-4.0, 0, 1.8), 0, 0.9)
    part(s, "Bush2", "nature/flower_bushes.glb", "Plant_Flowers", (3.0, 5, -14.2), 0, 1.0)
    part(s, "Bush3", "nature/bushes.glb", "Bush", (-3.2, 7.5, -46.0), 30, 0.8)
    prop(s, "Rock1", "props/rock.glb", (4.0, 0.1, -2.0), 45, 0.8)
    prop(s, "Rock2", "props/rock.glb", (-3.8, 7.6, -41.8), 10, 0.6)
    prop(s, "Sign1", "props/arrow_sign.glb", (2.0, 0, -3.4), 90, 0.6)
    prop(s, "Crate1", "props/crate.glb", (3.4, 5.35, -10.6), 20, 0.35)
    prop(s, "Bricks1", "props/bricks.glb", (-4.2, 9.5, -66.5), 0, 0.5)
    prop(s, "Bricks2", "props/bricks.glb", (4.2, 9.5, -66.5), 0, 0.5)
    prop(s, "Bricks3", "props/bricks.glb", (4.2, 10.5, -66.5), 15, 0.5)
    for i, (p, r) in enumerate([((-4.5, 0, -2.5), 0), ((3.3, 5, -9.2), 0), ((-3.0, 7, -29.4), 0), ((3.4, 7.5, -41.4), 0),
                                ((-2.6, 9, -68.6), 0), ((2.6, 9, -68.6), 0), ((0, 9, -60.3), 0)]):
        s.node(f"Lantern{i}", None, "Decor", instance=W + "Lantern.tscn", transform=xf(p, (0, r, 0)))

    s.node("Hazards", "Node3D")
    s.node("Bouncer", None, "Hazards", instance=G + "Bouncer.tscn", transform=xf((0, 0, -4.2)))
    s.node("SpinBar", None, "Hazards", instance=G + "SpinBar.tscn", transform=xf((0, 5.0, -12)), spin_degrees=vec3(0, 85, 0))
    s.node("Platform1", None, "Hazards", instance=G + "MovingPlatform.tscn", transform=xf((-3, 5.2, -19.5)),
           move_offset=vec3(6, 0, 0), move_time=2.0)
    s.node("Platform2", None, "Hazards", instance=G + "MovingPlatform.tscn", transform=xf((0, 5.2, -24.5)),
           move_offset=vec3(0, 2.5, 0), move_time=2.0, start_delay=1.0)
    for i, (x, z, d) in enumerate([(-1.6, -30.6, 0.0), (1.6, -30.6, 0.6), (0, -33.4, 1.2), (-3.0, -33.4, 1.8), (3.0, -33.4, 0.3)]):
        s.node(f"SpikeTrap{i}", None, "Hazards", instance=G + "SpikeTrap.tscn", transform=xf((x, 7.0, z)),
               start_delay=d, down_time=1.3, up_time=0.9)
    for i, (x, z) in enumerate([(-4.2, -32.0), (4.2, -32.0), (-2.2, -69.0), (2.2, -69.0)]):
        y = 7.0 if z > -50 else 9.0
        s.node(f"Spikes{i}", None, "Hazards", instance=G + "Spikes.tscn", transform=xf((x, y, z)))
    s.node("Saw1", None, "Hazards", instance=G + "SawBlade.tscn", transform=xf((-3, 7.9, -42.4)),
           move_offset=vec3(6, 0, 0), move_time=1.4)
    s.node("Saw2", None, "Hazards", instance=G + "SawBlade.tscn", transform=xf((3, 7.9, -45.2)),
           move_offset=vec3(-6, 0, 0), move_time=1.4, start_delay=0.7)
    s.node("SpikyBall", None, "Hazards", instance=G + "SpikyBall.tscn", transform=xf((0, 9.0, -64.5)), spin_degrees=vec3(0, 115, 0))
    s.node("Checkpoint1", None, "Hazards", instance=G + "Checkpoint.tscn", transform=xf((-3.2, 7.0, -28.8)))
    s.node("Checkpoint2", None, "Hazards", instance=G + "Checkpoint.tscn", transform=xf((3.0, 9.0, -60.2)))
    s.node("Door", None, instance=G + "Door.tscn", transform=xf((0, 9.0, -69.8)))

    s.node("Coins", "Node3D")
    for i, p in enumerate([(-2.5, 1.0, -2), (2.5, 1.0, -2), (-2.5, 5.9, -12), (2.5, 5.9, -12), (0, 6.4, -19.5),
                           (0, 8.8, -24.5), (0, 8.0, -32.0), (-3.0, 8.0, -35.6), (0, 8.5, -43.8), (-3.0, 8.5, -46.2),
                           (4.0, 9.2, -51), (1.0, 9.8, -56), (-3.5, 10.0, -63), (3.5, 10.0, -63)]):
        coin(s, i, p)

    s.node("Clouds", "Node3D")
    pink = (1.0, 0.82, 0.86)
    for i, (p, sz) in enumerate([((-10, -6, 2), 7), ((12, -9, -8), 9), ((-8, -8, -36), 10), ((14, -4, -58), 8),
                                 ((-22, 0, -48), 7), ((24, 2, -24), 6), ((0, -12, -80), 13), ((-30, 16, -80), 9),
                                 ((36, 18, -70), 10), ((-26, 20, -20), 8)]):
        cloud(s, f"Cloud{i}", p, sz, i + 20, col=pink)

    level_common(s, (0, 0.2, 2.5), -20)
    s.write("Scenes/Levels/level_2.tscn")


if __name__ == "__main__":
    player()
    saw_blade()
    spiky_ball()
    spin_bar()
    spike_trap()
    spikes()
    bouncer()
    moving_platform()
    checkpoint()
    door()
    lantern()
    theme()
    game_ui()
    menu_scene("Scenes/UI/win_screen.tscn", S + "UI/WinScreen.gd", "YOU WIN!",
               "The sky islands are safe again. Great job, hero!",
               [("PlayAgain", "Play Again")], stats=True,
               tint=((0.2, 0.14, 0.42), (1.0, 0.6, 0.45), (0.38, 0.24, 0.5)))
    level_1()
    level_2()
    print("Scenes generated.")
