extends Node3D

## Character showcase / start screen (Exercise 6).
## Lists every clip of the animation libraries on the character's
## AnimationPlayer (player / melee / shooter) as buttons. Drag to rotate the
## character, mouse wheel to zoom, "Play Game" starts level 1.

const TABS := [
	["Game", "player"],
	["Melee", "melee"],
	["Shooter", "shooter"],
]
const HIDDEN := ["RESET", "Armature|mixamo_com|Layer0"]

@onready var anim: AnimationPlayer = $Turntable/Hero/AnimationPlayer
@onready var turntable: Node3D = $Turntable
@onready var camera: Camera3D = $CameraPivot/Camera3D

var current := ""
var now_playing: Label
var dragging := false
var target_yaw := 0.0


func _ready() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	_build_ui()
	anim.animation_finished.connect(_on_finished)
	_play("player/Idle")


func _process(delta: float) -> void:
	turntable.rotation.y = lerp_angle(turntable.rotation.y, target_yaw, delta * 10.0)
	# keep the pivot upright in case a Flip was interrupted
	if not anim.is_playing() or not current.ends_with("Flip"):
		turntable.rotation.x = 0.0
		turntable.scale = Vector3.ONE


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			dragging = event.pressed
		elif event.button_index == MOUSE_BUTTON_WHEEL_UP and event.pressed:
			camera.position.z = max(1.8, camera.position.z - 0.25)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN and event.pressed:
			camera.position.z = min(6.0, camera.position.z + 0.25)
	elif event is InputEventMouseMotion and dragging:
		target_yaw += event.relative.x * 0.01


func _play(clip: String) -> void:
	current = clip
	anim.play(clip, 0.2)
	now_playing.text = "Now playing:  " + clip


# Library clips are mostly one-shots: replay them after a short pause.
func _on_finished(clip: StringName) -> void:
	if str(clip) != current:
		return
	await get_tree().create_timer(0.5).timeout
	if current == str(clip):
		anim.play(clip, 0.2)


# ---------------------------------------------------------------- UI
func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)

	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	panel.offset_left = 16
	panel.offset_top = 16
	panel.offset_bottom = -16
	panel.custom_minimum_size.x = 400
	layer.add_child(panel)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	panel.add_child(box)

	var title := Label.new()
	title.text = "MY CHARACTER"
	title.add_theme_font_size_override("font_size", 34)
	box.add_child(title)
	var sub := Label.new()
	sub.text = "Blender model + Mixamo skeleton\nGodot4-OpenAnimationLibraries"
	sub.add_theme_font_size_override("font_size", 16)
	box.add_child(sub)

	var tabs := TabContainer.new()
	tabs.size_flags_vertical = Control.SIZE_EXPAND_FILL
	tabs.add_theme_font_size_override("font_size", 18)
	box.add_child(tabs)

	for tab in TABS:
		var lib_name: String = tab[1]
		if not anim.has_animation_library(lib_name):
			continue
		var scroll := ScrollContainer.new()
		scroll.name = tab[0]
		scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		tabs.add_child(scroll)
		var list := VBoxContainer.new()
		list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		scroll.add_child(list)
		var names: Array = Array(anim.get_animation_library(lib_name).get_animation_list())
		names.sort_custom(func(a, b): return str(a).naturalnocasecmp_to(str(b)) < 0)
		for clip_name in names:
			var n := str(clip_name)
			# "root-*" clips are root-motion copies of the in-place ones
			if n in HIDDEN or n.begins_with("root-"):
				continue
			var b := Button.new()
			b.text = n
			b.alignment = HORIZONTAL_ALIGNMENT_LEFT
			b.add_theme_font_size_override("font_size", 17)
			b.pressed.connect(_play.bind(lib_name + "/" + n))
			list.add_child(b)

	var hint := Label.new()
	hint.text = "Drag = rotate   Wheel = zoom"
	hint.add_theme_font_size_override("font_size", 15)
	box.add_child(hint)

	var play := Button.new()
	play.text = "PLAY GAME"
	play.add_theme_font_size_override("font_size", 28)
	play.custom_minimum_size.y = 56
	play.pressed.connect(GameManager.start_game)
	box.add_child(play)

	now_playing = Label.new()
	now_playing.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	now_playing.grow_horizontal = Control.GROW_DIRECTION_BOTH
	now_playing.offset_top = -60
	now_playing.offset_left = 200
	now_playing.offset_right = 600
	now_playing.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	now_playing.add_theme_font_size_override("font_size", 24)
	now_playing.add_theme_color_override("font_outline_color", Color(0.1, 0.1, 0.2))
	now_playing.add_theme_constant_override("outline_size", 8)
	layer.add_child(now_playing)
