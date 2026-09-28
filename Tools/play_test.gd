extends SceneTree
# Automated logic test: coins -> door -> next level, hazards, spring, respawn, win screen.
var gm: Node
var failures := 0

func _initialize() -> void:
	gm = root.get_node("GameManager")
	_run()

func check(cond: bool, msg: String) -> void:
	print(("PASS  " if cond else "FAIL  ") + msg)
	if not cond: failures += 1

func frames(n: int) -> void:
	for i in n:
		await physics_frame

func player() -> CharacterBody3D:
	return get_first_node_in_group("Player")

func collect_all_coins() -> void:
	for c in get_nodes_in_group("Coin").duplicate():
		if is_instance_valid(c):
			player().global_position = c.global_position - Vector3.UP * 0.6
			player().velocity = Vector3.ZERO
			await frames(12)

func _run() -> void:
	await frames(5)
	# Exercise 6: the showcase is the start screen and holds all three libraries
	var main_scene: String = ProjectSettings.get_setting("application/run/main_scene")
	change_scene_to_file(main_scene)
	await frames(10)
	check(current_scene.scene_file_path.ends_with("showcase.tscn"), "Game opens on the character showcase")
	var sc_anim: AnimationPlayer = current_scene.get_node("Turntable/Hero/AnimationPlayer")
	check(sc_anim.has_animation("melee/Slash1") and sc_anim.has_animation("shooter/idle"),
		"Showcase has MeleeLib and ShooterLib clips")
	gm.start_game()
	await frames(80)
	check(current_scene.scene_file_path.ends_with("level_1.tscn"), "Game starts in level 1")
	check(gm.total_coins == 13, "Level 1 registers 13 coins (got %d)" % gm.total_coins)
	var p := player()
	await frames(30)
	check(p.is_on_floor(), "Player stands on the start island")
	check(p.animation.current_animation == "Idle", "Idle animation plays (got %s)" % p.animation.current_animation)

	# Retargeted animation really moves the Mixamo-rigged skeleton
	var sk: Skeleton3D = p.get_node("Model/FlipPivot/character").find_children("*", "Skeleton3D", true, false)[0]
	check(sk.name == "GeneralSkeleton" and sk.find_bone("LeftUpperArm") >= 0, "Skeleton retargeted with Mixamo BoneMap")
	var arm := sk.find_bone("LeftUpperArm")
	var moved := sk.get_bone_pose_rotation(arm).angle_to(sk.get_bone_rest(arm).basis.get_rotation_quaternion())
	check(moved > 0.3, "Idle clip bends the arm away from the T-pose (%.2f rad)" % moved)

	# Attack combo: punch -> punch -> kick
	p.perform_attack()
	await frames(3)
	check(p.animation.current_animation == "Attack1" and p.is_attacking, "Attack plays punch (got %s)" % p.animation.current_animation)
	p.perform_attack()
	await frames(3)
	check(p.animation.current_animation == "Attack2", "Second press chains the next hit")
	p.perform_attack()
	await frames(3)
	check(p.animation.current_animation == "Attack3", "Third press kicks")
	await frames(150)
	check(not p.is_attacking and p.animation.current_animation == "Idle", "Returns to Idle after the combo (got %s)" % p.animation.current_animation)

	# Locked door
	var door := current_scene.get_node("Door")
	p.global_position = door.global_position + door.global_basis.z * 1.2 + Vector3.UP * 0.2
	await frames(30)
	check(not door.is_open and current_scene.scene_file_path.ends_with("level_1.tscn"), "Door stays locked without coins")

	# Jump + flip
	p.global_position = Vector3(0, 0.2, 2.5)
	p.velocity = Vector3.ZERO
	await frames(20)
	p.perform_jump()
	await frames(2)
	check(p.animation.current_animation == "Jump" and p.velocity.y > 0, "Jump works")
	p.perform_flip_jump()
	await frames(3)
	check(p.animation.current_animation == "Flip", "Flip animation plays on double jump")
	await frames(40)

	# Hazard: spike trap should hurt + respawn
	var deaths: int = gm.deaths
	p.global_position = Vector3(0, 0.2, 2.5)
	p.set_checkpoint(Vector3(0, 0.2, 2.5))
	var saw := current_scene.get_node("Hazards/Saw1/Spin")
	p.global_position = saw.global_position
	await frames(60)
	check(gm.deaths == deaths + 1, "Saw blade hurts the player")
	check(p.global_position.distance_to(Vector3(0, 0.2, 2.5)) < 1.5, "Player respawns at checkpoint")

	# Falling into the void
	await frames(30)
	p.global_position = Vector3(0, -30, 0)
	await frames(60)
	check(gm.deaths == deaths + 2, "Dead zone catches falling player")

	# Moving platform carries the player
	var plat := current_scene.get_node("Hazards/Platform1")
	p.global_position = plat.global_position + Vector3.UP * 0.3
	p.velocity = Vector3.ZERO
	await frames(40)
	check(p.is_on_floor() and p.global_position.distance_to(plat.global_position) < 1.2, "Player rides the moving platform")

	await collect_all_coins()
	check(gm.score == gm.total_coins, "All level 1 coins collected (%d/%d)" % [gm.score, gm.total_coins])
	await frames(70)
	check(door.is_open, "Door opens after collecting all coins")
	p = player()
	p.global_position = door.global_position + door.global_basis.z * 0.8 + Vector3.UP * 0.2
	await frames(240)
	check(current_scene.scene_file_path.ends_with("level_2.tscn"), "Entering the open door loads level 2")
	check(gm.total_coins == 14, "Level 2 registers 14 coins (got %d)" % gm.total_coins)

	# Spring
	p = player()
	await frames(20)
	var bouncer := current_scene.get_node("Hazards/Bouncer")
	p.global_position = bouncer.global_position + Vector3.UP * 1.2
	p.velocity = Vector3.ZERO
	await frames(3)
	check(p.velocity.y > 10, "Spring launches the player (vy=%.1f)" % p.velocity.y)
	await frames(90)

	# Checkpoint
	var cp := current_scene.get_node("Hazards/Checkpoint1")
	p.global_position = cp.global_position + Vector3.UP * 0.3
	await frames(10)
	check(cp.reached and p.respawn_position.distance_to(cp.global_position) < 1.0, "Checkpoint sets respawn point")

	await collect_all_coins()
	check(gm.score == 14, "All level 2 coins collected (%d)" % gm.score)
	await frames(70)
	var door2 := current_scene.get_node("Door")
	check(door2.is_open, "Level 2 door opens")
	player().global_position = door2.global_position + door2.global_basis.z * 0.8 + Vector3.UP * 0.2
	await frames(240)
	check(current_scene.scene_file_path.ends_with("win_screen.tscn"), "Finishing level 2 shows the win screen")
	check(gm.total_score == 27, "Total coins counted across levels (got %d)" % gm.total_score)

	print("RESULT: %s (%d failures)" % ["OK" if failures == 0 else "FAILED", failures])
	quit(failures)
