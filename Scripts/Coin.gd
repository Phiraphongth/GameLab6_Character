extends Area3D

# ---------- VARIABLES ---------- #

# You can change these values from inspector!
@export_category("Properties")
@export var follow_speed := 6
@export var amplitude := 0.2
@export var frequency := 4

var time_passed = 0
var is_in_range = false
var is_shrinking = false

# Vector
var initial_position := Vector3.ZERO

@onready var player := get_tree().get_first_node_in_group("Player")

# ---------- FUNCTIONS ---------- #

func _init():
	add_to_group("Coin")

func _ready():
	initial_position = position
	time_passed = randf() * TAU # So coins don't all bob in sync

func _process(delta):
	coin_hover(delta) # Call the coin_hover function
	rotate_y(deg_to_rad(180) * delta)

	if is_in_range:
		if not is_shrinking:
			is_shrinking = true
			var tween = create_tween()
			tween.tween_property(self, "scale", Vector3.ONE * 0.3, 0.4).set_ease(Tween.EASE_IN_OUT)
		follow_player(delta)

# Coin Hover Animation
func coin_hover(delta):
	time_passed += delta
	if is_in_range:
		return
	var new_y = initial_position.y + amplitude * sin(frequency * time_passed)
	position.y = new_y

func follow_player(delta):
	var target = player.global_position + Vector3.UP * 0.7
	global_position += global_position.direction_to(target) * follow_speed * 2 * delta

# ---------- SIGNALS ---------- #

func _on_body_entered(body):
	# Delete The Coin and Add Score
	if body.is_in_group("Player"):
		GameManager.add_score()
		AudioManager.coin_sfx.play()
		queue_free()

func _on_range_body_entered(body):
	if body.is_in_group("Player"):
		is_in_range = true
