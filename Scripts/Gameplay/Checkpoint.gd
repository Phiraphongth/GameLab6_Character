extends Area3D

## Touch the flag to respawn here after falling or getting hurt.

var reached := false

@onready var flag: Node3D = $Flag


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	flag.scale = Vector3(1, 0.4, 1)


func _on_body_entered(body: Node3D) -> void:
	if reached or not body.is_in_group("Player"):
		return
	reached = true
	body.set_checkpoint(global_position + Vector3.UP * 0.5)
	AudioManager.coin_sfx.play()
	GameManager.hint.emit("Checkpoint!")
	var tween := create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(flag, "scale", Vector3.ONE, 0.5)
