extends Area3D

# ---------- SIGNALS ---------- #

func _ready():
	if not body_entered.is_connected(_on_body_entered):
		body_entered.connect(_on_body_entered)

func _on_body_entered(body):
	# Falling off the islands sends the player back to the last checkpoint
	if body.is_in_group("Player"):
		body.hurt()
