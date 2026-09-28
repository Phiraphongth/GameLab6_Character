@tool
extends StaticBody3D

## Low-poly tree built from primitives. Pine = stacked cones, Round = faceted blob.

enum Kind { PINE, ROUND }

@export var kind: Kind = Kind.ROUND: set = _set_kind
@export_range(1.0, 8.0, 0.1) var height := 3.0: set = _set_height
@export var leaf_color := Color(0.22, 0.58, 0.22): set = _set_leaf
@export var trunk_color := Color(0.45, 0.3, 0.2): set = _set_trunk
@export var variation := 0: set = _set_variation

var _mesh_instance: MeshInstance3D


func _ready() -> void:
	_rebuild()


func _rebuild() -> void:
	if not is_inside_tree():
		return
	if _mesh_instance == null:
		_mesh_instance = MeshInstance3D.new()
		add_child(_mesh_instance)
		var col := CollisionShape3D.new()
		var shape := CylinderShape3D.new()
		shape.radius = 0.25
		shape.height = 2.0
		col.shape = shape
		col.position.y = 1.0
		add_child(col)

	var mesh := ArrayMesh.new()
	var trunk_h := height * (0.35 if kind == Kind.PINE else 0.45)
	var trunk := CylinderMesh.new()
	trunk.top_radius = height * 0.04
	trunk.bottom_radius = height * 0.07
	trunk.height = trunk_h
	trunk.radial_segments = 5
	trunk.rings = 0
	LowPoly.add_surface(mesh, trunk, LowPoly.material(trunk_color),
			Transform3D(Basis(), Vector3(0, trunk_h * 0.5, 0)))

	var leaves := LowPoly.material(leaf_color, 0.8)
	if kind == Kind.PINE:
		var layers := 3
		for i in layers:
			var cone := CylinderMesh.new()
			var w := height * (0.36 - i * 0.08)
			cone.top_radius = 0.0
			cone.bottom_radius = w
			cone.height = height * 0.42
			cone.radial_segments = 7
			cone.rings = 0
			var y := trunk_h * 0.7 + i * height * 0.22 + cone.height * 0.5
			LowPoly.add_surface(mesh, cone, leaves,
					Transform3D(Basis(Vector3.UP, i * 0.4), Vector3(0, y, 0)), height * 0.02, variation + i)
	else:
		var blob := SphereMesh.new()
		blob.radius = height * 0.3
		blob.height = height * 0.5
		blob.radial_segments = 7
		blob.rings = 4
		LowPoly.add_surface(mesh, blob, leaves,
				Transform3D(Basis(), Vector3(0, trunk_h + height * 0.18, 0)), height * 0.05, variation)
		var blob2 := SphereMesh.new()
		blob2.radius = height * 0.18
		blob2.height = height * 0.3
		blob2.radial_segments = 6
		blob2.rings = 3
		LowPoly.add_surface(mesh, blob2, leaves,
				Transform3D(Basis(), Vector3(height * 0.2, trunk_h + height * 0.05, height * 0.08)), height * 0.04, variation + 3)
	_mesh_instance.mesh = mesh


func _set_kind(v: Kind) -> void: kind = v; _rebuild()
func _set_height(v: float) -> void: height = v; _rebuild()
func _set_leaf(v: Color) -> void: leaf_color = v; _rebuild()
func _set_trunk(v: Color) -> void: trunk_color = v; _rebuild()
func _set_variation(v: int) -> void: variation = v; _rebuild()
