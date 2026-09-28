extends Node3D

## Moves back and forth by `move_offset` and/or spins continuously.
## Works on any Node3D, including AnimatableBody3D moving platforms.

@export var move_offset := Vector3.ZERO
@export var move_time := 2.0          ## Seconds for one way
@export var spin_degrees := Vector3.ZERO ## Degrees per second on each axis
@export var start_delay := 0.0        ## Offsets the cycle so repeated movers aren't in sync

var _origin := Vector3.ZERO
var _time := 0.0


func _ready() -> void:
	_origin = position
	_time = start_delay


func _physics_process(delta: float) -> void:
	_time += delta
	if move_offset != Vector3.ZERO:
		var f := (1.0 - cos(_time * PI / move_time)) * 0.5
		position = _origin + move_offset * f
	if spin_degrees != Vector3.ZERO:
		rotation += spin_degrees * (PI / 180.0) * delta
