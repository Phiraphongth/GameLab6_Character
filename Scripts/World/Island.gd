@tool
extends StaticBody3D

## A floating sky island: grass top, dirt layer and a rocky cone underneath.
## The top surface is at local y = 0, so place the node where the player should stand.

@export_range(1.0, 30.0, 0.1) var radius := 5.0: set = _set_radius
@export_range(3, 16) var sides := 8: set = _set_sides
@export_range(1.0, 30.0, 0.1) var depth := 5.0: set = _set_depth
@export var grass_color := Color(0.36, 0.72, 0.24): set = _set_grass
@export var dirt_color := Color(0.5, 0.32, 0.2): set = _set_dirt
@export var rock_color := Color(0.46, 0.44, 0.52): set = _set_rock
@export var variation := 0: set = _set_variation

var _mesh_instance: MeshInstance3D
var _collision: CollisionShape3D


func _ready() -> void:
	_rebuild()


func _rebuild() -> void:
	if not is_inside_tree():
		return
	if _mesh_instance == null:
		_mesh_instance = MeshInstance3D.new()
		add_child(_mesh_instance)
		_collision = CollisionShape3D.new()
		add_child(_collision)

	var mesh := ArrayMesh.new()
	var grass := CylinderMesh.new()
	grass.top_radius = radius
	grass.bottom_radius = radius * 1.02
	grass.height = 0.45
	grass.radial_segments = sides
	grass.rings = 0
	LowPoly.add_surface(mesh, grass, LowPoly.material(grass_color),
			Transform3D(Basis(), Vector3(0, -0.225, 0)), 0.0)

	var dirt := CylinderMesh.new()
	dirt.top_radius = radius * 1.02
	dirt.bottom_radius = radius * 0.85
	dirt.height = 0.9
	dirt.radial_segments = sides
	dirt.rings = 1
	LowPoly.add_surface(mesh, dirt, LowPoly.material(dirt_color),
			Transform3D(Basis(), Vector3(0, -0.9, 0)), radius * 0.02, variation, true)

	var rock := CylinderMesh.new()
	rock.top_radius = radius * 0.85
	rock.bottom_radius = max(radius * 0.08, 0.2)
	rock.height = depth
	rock.radial_segments = sides
	rock.rings = 3
	LowPoly.add_surface(mesh, rock, LowPoly.material(rock_color),
			Transform3D(Basis(), Vector3(0, -1.35 - depth * 0.5, 0)), radius * 0.09, variation + 7, true)

	_mesh_instance.mesh = mesh

	# Collision matches the polygonal top exactly (a cylinder shape would stick out).
	var top := CylinderMesh.new()
	top.top_radius = radius
	top.bottom_radius = radius * 0.85
	top.height = 1.35
	top.radial_segments = sides
	top.rings = 0
	var shape := ConvexPolygonShape3D.new()
	var pts := PackedVector3Array()
	for p in top.get_mesh_arrays()[Mesh.ARRAY_VERTEX]:
		pts.append(p + Vector3(0, -0.675, 0))
	shape.points = pts
	_collision.shape = shape


func _set_radius(v: float) -> void: radius = v; _rebuild()
func _set_sides(v: int) -> void: sides = v; _rebuild()
func _set_depth(v: float) -> void: depth = v; _rebuild()
func _set_grass(v: Color) -> void: grass_color = v; _rebuild()
func _set_dirt(v: Color) -> void: dirt_color = v; _rebuild()
func _set_rock(v: Color) -> void: rock_color = v; _rebuild()
func _set_variation(v: int) -> void: variation = v; _rebuild()
