# ----------------------------------------------------------------------------------- #
# -------------- FEEL FREE TO USE IN ANY PROJECT, COMMERCIAL OR NON-COMMERCIAL ------ #
# ---------------------- 3D PLATFORMER CONTROLLER BY SD STUDIOS --------------------- #
# ---------------------------- ATTRIBUTION NOT REQUIRED ----------------------------- #
# ----------------------------------------------------------------------------------- #
# Modified (Exercise 6): the player is our own character made in Blender with a
# Mixamo skeleton, animated with Godot4-OpenAnimationLibraries (Melee/Shooter).
# Animations keep the Starter Kit names (Idle / Run / Jump / Fall / Flip ...),
# see Tools/build_player6_animations.gd. Added attack combo, hurt/respawn,
# bouncers and victory.

extends CharacterBody3D

# ---------- VARIABLES ---------- #

@export_category("Player Properties")
@export var move_speed : float = 6
@export var jump_force : float = 5
@export var follow_lerp_factor : float = 4
@export var jump_limit : int = 2

@export_group("Game Juice")
@export var jumpStretchSize := Vector3(0.8, 1.2, 0.8)

# Booleans
var is_grounded = false
var can_double_jump = false
var is_flipping = false
var is_attacking = false
var combo_step = 0
var can_move = true
var was_on_floor = true

var respawn_position := Vector3.ZERO

# Onready Variables
@onready var model = $Model
@onready var animation = $Model/AnimationPlayer
@onready var spring_arm = %Gimbal

@onready var particle_trail = $ParticleTrail
@onready var footsteps = $Footsteps

# Get the gravity from the project settings to be synced with RigidBody nodes.
var gravity = ProjectSettings.get_setting("physics/3d/default_gravity") * 2

# ---------- FUNCTIONS ---------- #

func _ready():
	respawn_position = global_position
	animation.play("Idle")

func _process(delta):
	# Smoothly follow player's position
	spring_arm.position = lerp(spring_arm.position, position, delta * follow_lerp_factor)

	# Player Rotation
	if is_moving() and can_move:
		var look_direction = Vector2(velocity.z, velocity.x)
		model.rotation.y = lerp_angle(model.rotation.y, look_direction.angle(), delta * 12)

func _physics_process(delta):
	get_input(delta)
	player_animations()

	# Check if player is grounded or not
	is_grounded = true if is_on_floor() else false

	# Handle Jumping
	if is_grounded:
		can_double_jump = true

	if Input.is_action_just_pressed("jump") and can_move:
		if is_on_floor():
			perform_jump()
		elif can_double_jump:
			if is_moving():
				perform_flip_jump()

	if Input.is_action_just_pressed("attack") and can_move and not is_flipping:
		perform_attack()

	# Small landing squash
	if is_grounded and not was_on_floor:
		landTween()
	was_on_floor = is_grounded

	velocity.y -= gravity * delta

func perform_jump():
	AudioManager.jump_sfx.play()
	AudioManager.jump_sfx.pitch_scale = 1.12

	jumpTween()
	animation.play("Jump")
	velocity.y = jump_force

func perform_flip_jump():
	AudioManager.jump_sfx.play()
	AudioManager.jump_sfx.pitch_scale = 0.8
	can_double_jump = false
	is_flipping = true
	animation.play("Flip", -1, 1.4)
	velocity.y = jump_force
	await animation.animation_finished
	is_flipping = false

# Punch -> punch -> kick on the ground, a jumping slash in the air.
# Pressing again while the current hit is playing chains the next one.
func perform_attack():
	if is_attacking and combo_step >= 3:
		return
	var clip: String
	if is_on_floor():
		combo_step = combo_step + 1 if is_attacking else 1
		clip = "Attack%d" % combo_step
	else:
		if is_attacking:
			return
		combo_step = 3
		clip = "AirAttack"
	is_attacking = true
	AudioManager.jump_sfx.pitch_scale = 1.6
	AudioManager.jump_sfx.play()
	animation.play(clip, 0.1, 1.3)
	var step = combo_step
	await animation.animation_finished
	# Only the last hit of a chain ends the attack
	if step == combo_step:
		is_attacking = false
		combo_step = 0

func is_moving():
	return abs(velocity.z) > 0 || abs(velocity.x) > 0

func jumpTween():
	var tween = get_tree().create_tween()
	tween.tween_property(self, "scale", jumpStretchSize, 0.1)
	tween.tween_property(self, "scale", Vector3(1,1,1), 0.1)

func landTween():
	var tween = get_tree().create_tween()
	tween.tween_property(model, "scale", Vector3(1.15, 0.85, 1.15), 0.06)
	tween.tween_property(model, "scale", Vector3.ONE, 0.12)

# Get Player Input
func get_input(_delta):
	var move_direction := Vector3.ZERO
	if can_move:
		move_direction.x = Input.get_axis("move_left", "move_right")
		move_direction.z = Input.get_axis("move_forward", "move_back")

	# Move The player Towards Spring Arm/Camera Rotation
	move_direction = move_direction.rotated(Vector3.UP, spring_arm.rotation.y).normalized()
	velocity = Vector3(move_direction.x * move_speed, velocity.y, move_direction.z * move_speed)

	move_and_slide()

# Handle Player Animations
func player_animations():
	particle_trail.emitting = false
	footsteps.stream_paused = true

	if not can_move or is_flipping or is_attacking:
		return

	if is_on_floor():
		if is_moving(): # Checks if player is moving
			animation.play("Run", 0.2)
			particle_trail.emitting = true
			footsteps.stream_paused = false
		else:
			animation.play("Idle", 0.3)
	elif velocity.y < 0:
		animation.play("Fall", 0.3)

# ---------- GAMEPLAY ---------- #

# Launch the player upward (used by the spring / bouncer)
func bounce(force: float):
	velocity.y = force
	can_double_jump = true
	jumpTween()
	animation.play("Jump")

# Called by hazards and the dead zone
func hurt():
	if not can_move:
		return
	can_move = false
	is_flipping = false
	is_attacking = false
	GameManager.add_death()
	AudioManager.hurt_sfx.play()
	animation.play("Hurt")
	velocity = Vector3(0, jump_force * 0.6, 0)
	var tween = get_tree().create_tween()
	tween.tween_property(model, "scale", Vector3(1.3, 0.7, 1.3), 0.08)
	tween.tween_property(model, "scale", Vector3.ONE, 0.2)
	await get_tree().create_timer(0.6).timeout
	respawn()

func respawn():
	global_position = respawn_position
	velocity = Vector3.ZERO
	model.scale = Vector3.ONE
	$Model/FlipPivot.rotation.x = 0
	$Model/FlipPivot.scale = Vector3.ONE
	animation.play("Idle")
	can_move = true
	# Blink for a moment so the respawn is noticeable
	for i in 6:
		model.visible = not model.visible
		await get_tree().create_timer(0.08).timeout
	model.visible = true

func set_checkpoint(point: Vector3):
	respawn_position = point

# Called when entering an open door
func victory():
	can_move = false
	velocity = Vector3.ZERO
	animation.play("VictorySign", 0.2)
	var camera_yaw = spring_arm.rotation.y
	var tween = get_tree().create_tween()
	tween.tween_property(model, "rotation:y", camera_yaw, 0.3)
