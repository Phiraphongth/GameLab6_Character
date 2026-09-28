extends Area3D

## Anything that hurts the player on touch (spikes, saw blades, spiky balls ...).

@export var active := true


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _physics_process(_delta: float) -> void:
	# Also catch a player who is standing still inside a trap that just switched on
	if active:
		for body in get_overlapping_bodies():
			_on_body_entered(body)


func _on_body_entered(body: Node3D) -> void:
	if active and body.is_in_group("Player"):
		body.hurt()
