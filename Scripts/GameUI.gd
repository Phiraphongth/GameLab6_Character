extends CanvasLayer

# ---------- VARIABLES ---------- #

@onready var coinsLabel: Label = $HUD/CoinsLabel
@onready var levelLabel: Label = $HUD/LevelLabel
@onready var statsLabel: Label = $HUD/StatsLabel
@onready var hintLabel: Label = $HUD/HintLabel
@onready var pauseMenu: Control = $PauseMenu

var _hint_tween: Tween

# ---------- FUNCTIONS ---------- #

func _ready():
	process_mode = Node.PROCESS_MODE_ALWAYS
	pauseMenu.visible = false
	hintLabel.modulate.a = 0.0
	GameManager.score_changed.connect(_on_score_changed)
	GameManager.hint.connect(show_hint)
	_on_score_changed(GameManager.score, GameManager.total_coins)
	$PauseMenu/Center/Box/VBox/Resume.pressed.connect(toggle_pause)
	$PauseMenu/Center/Box/VBox/Restart.pressed.connect(GameManager.restart_level)
	var showcase := Button.new()
	showcase.text = "Main Menu"
	showcase.pressed.connect(GameManager.open_showcase)
	$PauseMenu/Center/Box/VBox.add_child(showcase)

	var level = get_tree().current_scene
	if "level_name" in level:
		levelLabel.text = level.level_name
	var tween = create_tween()
	tween.tween_interval(3.0)
	tween.tween_property(levelLabel, "modulate:a", 0.0, 1.0)

func _process(_delta):
	statsLabel.text = "Time %s   Falls %d" % [GameManager.format_time(GameManager.run_time), GameManager.deaths]

func _unhandled_input(event):
	if event.is_action_pressed("mouse_visible") or event.is_action_pressed("pause"):
		toggle_pause()
	elif event is InputEventMouseButton and event.pressed and not get_tree().paused:
		# Browsers only allow capturing the mouse after a click
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func toggle_pause():
	var paused = not get_tree().paused
	get_tree().paused = paused
	pauseMenu.visible = paused
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE if paused else Input.MOUSE_MODE_CAPTURED)
	if paused:
		$PauseMenu/Center/Box/VBox/Resume.grab_focus()

func _on_score_changed(score: int, total: int):
	coinsLabel.text = "%d / %d" % [score, total] # Set the coin label text to the score variable
	var tween = create_tween()
	coinsLabel.pivot_offset = coinsLabel.size * 0.5
	tween.tween_property(coinsLabel, "scale", Vector2.ONE * 1.25, 0.08)
	tween.tween_property(coinsLabel, "scale", Vector2.ONE, 0.15)

func show_hint(text: String):
	hintLabel.text = text
	if _hint_tween:
		_hint_tween.kill()
	_hint_tween = create_tween()
	_hint_tween.tween_property(hintLabel, "modulate:a", 1.0, 0.2)
	_hint_tween.tween_interval(3.0)
	_hint_tween.tween_property(hintLabel, "modulate:a", 0.0, 0.6)
