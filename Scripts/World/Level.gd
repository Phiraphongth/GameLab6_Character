extends Node3D

## Root script of every level: registers the coin count and shows the intro text.

@export var level_name := "Level"
@export_multiline var intro_hint := ""


func _ready() -> void:
	var coins := get_tree().get_nodes_in_group("Coin").size()
	GameManager.register_level(coins)
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	await get_tree().create_timer(0.6).timeout
	if intro_hint != "":
		GameManager.hint.emit(intro_hint)
