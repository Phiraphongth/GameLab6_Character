# Saves screenshots of the showcase and of gameplay into Screenshots/.
# Needs a real window (not --headless):
#   Godot --path . -s Tools/capture_screenshots.gd
extends SceneTree

const OUT := "res://Screenshots/"
var gm: Node


func _initialize() -> void:
	gm = root.get_node("GameManager")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	root.size = Vector2i(1280, 720)
	_run()


func frames(n: int) -> void:
	for i in n:
		await process_frame


func shot(file: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(OUT + file)
	print("saved ", file)


func _run() -> void:
	change_scene_to_file("res://Scenes/UI/showcase.tscn")
	await frames(30)
	await shot("01_start_screen.png")

	gm.start_game()
	await create_timer(2.5).timeout
	var p: CharacterBody3D = get_first_node_in_group("Player")
	Input.action_press("move_right")
	await create_timer(0.45).timeout
	await shot("06_game_run.png")
	Input.action_release("move_right")
	await create_timer(0.5).timeout
	p.perform_attack()
	await create_timer(0.35).timeout
	p.perform_attack()
	await create_timer(0.3).timeout
	await shot("07_game_attack.png")
	await create_timer(1.5).timeout
	p.perform_jump()
	await create_timer(0.2).timeout
	p.velocity.x = 3
	p.perform_flip_jump()
	await create_timer(0.2).timeout
	await shot("08_game_flip.png")
	quit()
