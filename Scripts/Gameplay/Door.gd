extends Node3D

## The exit door. Locked until every coin in the level is collected.

@onready var left_leaf: Node3D = $LeftHinge
@onready var right_leaf: Node3D = $RightHinge
@onready var portal: MeshInstance3D = $Portal
@onready var lock_icon: Node3D = $Lock
@onready var light: OmniLight3D = $Light
@onready var sparkles: CPUParticles3D = $Sparkles
@onready var trigger: Area3D = $Trigger

var is_open := false
var _used := false


func _ready() -> void:
	trigger.body_entered.connect(_on_body_entered)
	GameManager.all_coins_collected.connect(open)
	portal.visible = false
	light.visible = false
	sparkles.emitting = false


func _process(delta: float) -> void:
	lock_icon.rotate_y(delta * 1.5)


func open() -> void:
	if is_open:
		return
	is_open = true
	$Blocker/CollisionShape3D.set_deferred("disabled", true)
	AudioManager.door_sfx.play()
	portal.visible = true
	portal.scale = Vector3.ONE * 0.01
	light.visible = true
	sparkles.emitting = true
	var tween := create_tween().set_parallel().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(left_leaf, "rotation_degrees:y", -105.0, 1.0)
	tween.tween_property(right_leaf, "rotation_degrees:y", 105.0, 1.0)
	tween.tween_property(lock_icon, "scale", Vector3.ONE * 0.01, 0.4)
	tween.tween_property(portal, "scale", Vector3.ONE, 0.8)


func _on_body_entered(body: Node3D) -> void:
	if not body.is_in_group("Player") or _used:
		return
	if not is_open:
		GameManager.hint.emit("The door is locked! Coins: %d / %d" % [GameManager.score, GameManager.total_coins])
		return
	_used = true
	body.victory()
	AudioManager.door_sfx.play()
	GameManager.hint.emit("Level complete!")
	await get_tree().create_timer(1.6).timeout
	GameManager.complete_level()
