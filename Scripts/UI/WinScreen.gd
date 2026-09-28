extends Node3D

## Shown after the last level.

@onready var ninja_anim: AnimationPlayer = $Ninja/AnimationPlayer
@onready var camera_pivot: Node3D = $CameraPivot


func _ready() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	ninja_anim.play("VictorySign")
	$UI/Center/VBox/Stats.text = "Coins  %d\nTime  %s\nFalls  %d" % [
		GameManager.total_score, GameManager.format_time(GameManager.run_time), GameManager.deaths]
	$UI/Center/VBox/PlayAgain.pressed.connect(GameManager.start_game)
	$UI/Center/VBox/PlayAgain.grab_focus()


func _process(delta: float) -> void:
	camera_pivot.rotate_y(delta * 0.12)
