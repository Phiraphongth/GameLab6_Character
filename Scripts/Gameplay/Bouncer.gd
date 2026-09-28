extends Area3D

## Spring that launches the player high into the air.

@export var force := 15.0

@onready var anim: AnimationPlayer = $Model/AnimationPlayer


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	anim.play("Bouncer_Idle")


func _on_body_entered(body: Node3D) -> void:
	if body.is_in_group("Player") and body.can_move:
		body.bounce(force)
		AudioManager.bounce_sfx.play()
		anim.play("Bouncer_Bounce")
		anim.queue("Bouncer_Idle")
