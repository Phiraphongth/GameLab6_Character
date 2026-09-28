class_name LowPoly
extends RefCounted

## Helpers that turn Godot primitive meshes into flat-shaded, slightly
## jittered "low-poly" surfaces. Used by Island, LowPolyTree and CloudPuff.


static func material(color: Color, rough := 0.9, emission := 0.0) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = rough
	if emission > 0.0:
		mat.emission_enabled = true
		mat.emission = color
		mat.emission_energy_multiplier = emission
	return mat


## Appends `primitive` as a new flat-shaded surface on `target`.
## `xf` positions it, `jitter` randomly moves vertices (same position -> same offset
## so the mesh stays watertight).
static func add_surface(target: ArrayMesh, primitive: PrimitiveMesh, mat: Material,
		xf := Transform3D.IDENTITY, jitter := 0.0, rng_seed := 0, keep_top := false) -> void:
	var arrays := primitive.get_mesh_arrays()
	var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
	var offsets := {}
	var rng := RandomNumberGenerator.new()

	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	st.set_smooth_group(0xFFFFFFFF) # flat shading
	var count := indices.size() if indices.size() > 0 else verts.size()
	for i in count:
		var v: Vector3 = verts[indices[i]] if indices.size() > 0 else verts[i]
		if jitter > 0.0:
			var key := Vector3i((v * 1000.0).round())
			if not offsets.has(key):
				rng.seed = hash(key) + rng_seed
				var o := Vector3(rng.randf_range(-1, 1), rng.randf_range(-1, 1), rng.randf_range(-1, 1)) * jitter
				if keep_top and v.y >= primitive.get_aabb().end.y - 0.001:
					o.y = 0.0
				offsets[key] = o
			v += offsets[key]
		st.add_vertex(xf * v)
	st.generate_normals()
	st.set_material(mat)
	st.commit(target)
