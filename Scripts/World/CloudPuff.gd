@tool
extends Node3D

## A fluffy low-poly cloud made of a few flattened spheres. Slowly drifts and bobs.

@export_range(0.5, 20.0, 0.1) var size := 3.0: set = _set_size
@export var color := Color(1, 1, 1): set = _set_color
@export var variation := 0: set = _set_variation
@export var drift := 0.4

var _mesh_instance: MeshInstance3D
var _time := 0.0
var _origin := Vector3.ZERO


func _ready() -> void:
	_origin = position
	_time = variation * 1.7
	_rebuild()


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	_time += delta
	position = _origin + Vector3(sin(_time * 0.15) * drift * size, sin(_time * 0.5) * 0.15 * size, 0)


func _rebuild() -> void:
	if not is_inside_tree():
		return
	if _mesh_instance == null:
		_mesh_instance = MeshInstance3D.new()
		_mesh_instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(_mesh_instance)
	var mat := LowPoly.material(color, 1.0)
	mat.rim_enabled = true
	mat.rim = 0.6
	var mesh := ArrayMesh.new()
	var rng := RandomNumberGenerator.new()
	rng.seed = variation
	var puffs := 4 + rng.randi() % 3
	for i in puffs:
		var s := SphereMesh.new()
		var r := size * rng.randf_range(0.35, 0.6)
		s.radius = r
		s.height = r * 1.3
		s.radial_segments = 7
		s.rings = 3
		var x := (float(i) / (puffs - 1) - 0.5) * size * 1.6
		var p := Vector3(x, rng.randf_range(0.0, 0.3) * size, rng.randf_range(-0.3, 0.3) * size)
		LowPoly.add_surface(mesh, s, mat, Transform3D(Basis(), p), 0.0)
	_mesh_instance.mesh = mesh


func _set_size(v: float) -> void: size = v; _rebuild()
func _set_color(v: Color) -> void: color = v; _rebuild()
func _set_variation(v: int) -> void: variation = v; _rebuild()
