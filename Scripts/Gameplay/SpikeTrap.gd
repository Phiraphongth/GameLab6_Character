extends Node3D

## Spikes pop out of the floor on a timer. Only dangerous while raised.

@export var down_time := 1.6
@export var up_time := 1.0
@export var start_delay := 0.0

@onready var hazard: Area3D = $Hazard
@onready var anim: AnimationPlayer = $Model/AnimationPlayer
@onready var warning: MeshInstance3D = $Warning

const CLIP := "SpikeTrap_Activate"


func _ready() -> void:
	hazard.active = false
	anim.play(CLIP)
	anim.seek(0.0, true)
	anim.pause()
	_cycle()


func _cycle() -> void:
	await get_tree().create_timer(start_delay + 0.01).timeout
	while is_inside_tree():
		await get_tree().create_timer(down_time - 0.4).timeout
		# Short warning flash before the spikes come up
		warning.visible = true
		await get_tree().create_timer(0.4).timeout
		warning.visible = false
		anim.play(CLIP)
		await get_tree().create_timer(0.12).timeout
		hazard.active = true
		await get_tree().create_timer(up_time).timeout
		hazard.active = false
		anim.play_backwards(CLIP)
