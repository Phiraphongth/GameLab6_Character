# Run once from the command line:
#   Godot --headless --path . -s Tools/build_player6_animations.gd
#
# Builds res://Assets/Models/player6/player6_animations.res for the Exercise 6
# character. Clips are taken from Godot4-OpenAnimationLibraries (MeleeLib.res,
# ShooterLib.res) and renamed to the names Scripts/player.gd already uses
# (Idle, Run, Jump, Fall, Flip, Hurt, VictorySign ...).
#
# The library tracks target "%GeneralSkeleton:<Bone>". The character is imported
# with "Mixamo BoneMap.tres", which renames its skeleton to GeneralSkeleton, so
# the tracks work unchanged as long as the AnimationPlayer's root_node is the
# character scene root (Player/Model/FlipPivot/character).
extends SceneTree

const MELEE := "res://Assets/Animations/MeleeLib.res"
const SHOOTER := "res://Assets/Animations/ShooterLib.res"
const CHARACTER := "res://Assets/Models/player6/character.glb"
const OUTPUT := "res://Assets/Models/player6/player6_animations.res"

# Player name -> [library, clip, loop?]
const MAP := {
	"Idle": [SHOOTER, "idle", true],
	"Walk": [SHOOTER, "walk", true],
	"Run": [SHOOTER, "run_067", true],
	"Jump": [SHOOTER, "jump", false],
	"Fall": [SHOOTER, "fall", true],
	"Land": [SHOOTER, "fall-landing", false],
	"Hurt": [SHOOTER, "hurt1", false],
	"Death": [SHOOTER, "die1", false],
	"VictorySign": [SHOOTER, "handsup-idle", true],
	# attacks (left mouse / F): punch -> punch -> kick combo, slash in the air
	"Attack1": [SHOOTER, "punchright", false],
	"Attack2": [SHOOTER, "punchleft", false],
	"Attack3": [SHOOTER, "kick1", false],
	"AirAttack": [MELEE, "LightJumpAttack", false],
}


func _init() -> void:
	var bones := _skeleton_bones()
	var lib := AnimationLibrary.new()

	for new_name in MAP:
		var info: Array = MAP[new_name]
		var src: AnimationLibrary = load(info[0])
		var anim: Animation = src.get_animation(info[1]).duplicate(true)
		_strip_missing_bones(anim, bones)
		anim.loop_mode = Animation.LOOP_LINEAR if info[2] else Animation.LOOP_NONE
		lib.add_animation(new_name, anim)

	# Flip (double jump): the jump pose + a 360 degree spin of FlipPivot,
	# which is the parent of the character root.
	var flip: Animation = lib.get_animation("Jump").duplicate(true)
	flip.length = 0.5
	flip.loop_mode = Animation.LOOP_NONE
	var t := flip.add_track(Animation.TYPE_VALUE)
	flip.track_set_path(t, "..:rotation:x")
	flip.track_set_interpolation_type(t, Animation.INTERPOLATION_CUBIC)
	flip.track_insert_key(t, 0.0, 0.0)
	flip.track_insert_key(t, 0.25, PI)
	flip.track_insert_key(t, 0.5, TAU)
	var s := flip.add_track(Animation.TYPE_VALUE)
	flip.track_set_path(s, "..:scale")
	flip.track_insert_key(s, 0.0, Vector3.ONE)
	flip.track_insert_key(s, 0.25, Vector3(1.0, 0.85, 1.0))
	flip.track_insert_key(s, 0.5, Vector3.ONE)
	lib.add_animation("Flip", flip)

	# RESET keeps the pivot upright if a flip gets interrupted.
	var reset := Animation.new()
	reset.length = 0.001
	var r := reset.add_track(Animation.TYPE_VALUE)
	reset.track_set_path(r, "..:rotation:x")
	reset.track_insert_key(r, 0.0, 0.0)
	var rs := reset.add_track(Animation.TYPE_VALUE)
	reset.track_set_path(rs, "..:scale")
	reset.track_insert_key(rs, 0.0, Vector3.ONE)
	lib.add_animation("RESET", reset)

	var err := ResourceSaver.save(lib, OUTPUT)
	print("Saved ", OUTPUT, " err=", err, " animations=", lib.get_animation_list())
	quit()


func _skeleton_bones() -> Dictionary:
	var scene: Node = load(CHARACTER).instantiate()
	var sk: Skeleton3D = scene.find_children("*", "Skeleton3D", true, false)[0]
	var bones := {}
	for i in sk.get_bone_count():
		bones[sk.get_bone_name(i)] = true
	scene.free()
	return bones


# Drop tracks for bones our skeleton doesn't have (fingers, Weapon, Root ...)
# so the AnimationPlayer doesn't warn about unresolved tracks.
func _strip_missing_bones(anim: Animation, bones: Dictionary) -> void:
	for i in range(anim.get_track_count() - 1, -1, -1):
		var path := anim.track_get_path(i)
		if path.get_subname_count() > 0 and not bones.has(str(path.get_subname(0))):
			anim.remove_track(i)
