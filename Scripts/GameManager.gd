extends Node

# ---------- SIGNALS ---------- #

signal score_changed(score: int, total: int)
signal all_coins_collected
signal hint(text: String)

# ---------- VARIABLES ---------- #

const WIN_SCREEN := "res://Scenes/UI/win_screen.tscn"
const SHOWCASE := "res://Scenes/UI/showcase.tscn"
const LEVELS: Array[String] = [
	"res://Scenes/Levels/level_1.tscn",
	"res://Scenes/Levels/level_2.tscn",
]

var score := 0            # Coins collected in the current level
var total_coins := 0      # Coins that exist in the current level
var current_level := -1
var total_score := 0      # Coins collected across the whole run
var deaths := 0
var run_time := 0.0
var timer_running := false

var _fade_layer: CanvasLayer
var _fade_rect: ColorRect
var _loading_label: Label
var _changing := false

# ---------- FUNCTIONS ---------- #

func _init() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_fade_layer = CanvasLayer.new()
	_fade_layer.layer = 100
	add_child(_fade_layer)
	_fade_rect = ColorRect.new()
	_fade_rect.color = Color(0.05, 0.07, 0.15, 0.0)
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade_layer.add_child(_fade_rect)
	_loading_label = Label.new()
	_loading_label.text = "Loading..."
	_loading_label.add_theme_font_size_override("font_size", 40)
	_loading_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_loading_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_loading_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	_loading_label.modulate.a = 0.0
	_fade_rect.add_child(_loading_label)


func _process(delta: float) -> void:
	if timer_running and not get_tree().paused:
		run_time += delta


# Called by Level.gd when a level finishes loading.
func register_level(coin_count: int) -> void:
	score = 0
	total_coins = coin_count
	timer_running = true
	var path := get_tree().current_scene.scene_file_path
	current_level = LEVELS.find(path)
	score_changed.emit(score, total_coins)


func add_score() -> void:
	score += 1
	total_score += 1
	score_changed.emit(score, total_coins)
	if score == total_coins:
		all_coins_collected.emit()
		hint.emit("All coins collected! The door is open!")


func has_all_coins() -> bool:
	return score >= total_coins


func add_death() -> void:
	deaths += 1


func start_game() -> void:
	total_score = 0
	deaths = 0
	run_time = 0.0
	change_scene(LEVELS[0])


func open_showcase() -> void:
	timer_running = false
	change_scene(SHOWCASE)


func restart_level() -> void:
	# Coins collected in this attempt don't count twice.
	total_score -= score
	change_scene(get_tree().current_scene.scene_file_path)


func complete_level() -> void:
	var next := current_level + 1
	if next < LEVELS.size():
		change_scene(LEVELS[next])
	else:
		timer_running = false
		change_scene(WIN_SCREEN)


func change_scene(path: String) -> void:
	if _changing:
		return
	_changing = true
	var tween := create_tween()
	tween.tween_property(_fade_rect, "color:a", 1.0, 0.45)
	tween.tween_property(_loading_label, "modulate:a", 1.0, 0.1)
	await tween.finished
	# Give the browser one frame to draw the loading text before the (blocking) load
	await get_tree().process_frame
	await get_tree().process_frame
	get_tree().paused = false
	get_tree().change_scene_to_file(path)
	await get_tree().process_frame
	await get_tree().process_frame
	_loading_label.modulate.a = 0.0
	var tween_in := create_tween()
	tween_in.tween_property(_fade_rect, "color:a", 0.0, 0.45)
	_changing = false


func format_time(seconds: float) -> String:
	return "%02d:%02d" % [int(seconds) / 60, int(seconds) % 60]
