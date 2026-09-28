@tool
extends Node3D

## Put this on an instanced multi-model .glb (e.g. nature/bushes.glb) to show
## only one of its meshes, moved to this node's origin.

@export var part := "": set = _set_part


func _ready() -> void:
	_apply()


func _apply() -> void:
	if not is_inside_tree() or part == "":
		return
	for mesh in find_children("*", "MeshInstance3D", true, false):
		var show := mesh.name == part
		mesh.visible = show
		if show:
			mesh.position = Vector3.ZERO


func _set_part(v: String) -> void:
	part = v
	_apply()
