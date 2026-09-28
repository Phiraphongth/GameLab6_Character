extends Node3D

## Start screen (Exercise 6): shows the player character on a small island
## with a "Play Game" button. Drag to rotate the character.

@onready var anim: AnimationPlayer = $Turntable/Hero/AnimationPlayer
@onready var turntable: Node3D = $Turntable

var dragging := false
var target_yaw := 0.0


func _ready() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	_build_ui()
	anim.play("player/Idle")


func _process(delta: float) -> void:
	if not dragging:
		target_yaw += delta * 0.4
	turntable.rotation.y = lerp_angle(turntable.rotation.y, target_yaw, delta * 10.0)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		dragging = event.pressed
	elif event is InputEventMouseMotion and dragging:
		target_yaw += event.relative.x * 0.01


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)

	var title := Label.new()
	title.text = "SKY NINJA 2"
	title.set_anchors_preset(Control.PRESET_CENTER_TOP)
	title.grow_horizontal = Control.GROW_DIRECTION_BOTH
	title.offset_top = 40
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 72)
	title.add_theme_color_override("font_outline_color", Color(0.1, 0.1, 0.2))
	title.add_theme_constant_override("outline_size", 14)
	layer.add_child(title)

	var play := Button.new()
	play.text = "PLAY GAME"
	play.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	play.grow_horizontal = Control.GROW_DIRECTION_BOTH
	play.grow_vertical = Control.GROW_DIRECTION_BEGIN
	play.offset_bottom = -50
	play.custom_minimum_size = Vector2(320, 70)
	play.add_theme_font_size_override("font_size", 34)
	play.pressed.connect(GameManager.start_game)
	layer.add_child(play)
	play.grab_focus()
