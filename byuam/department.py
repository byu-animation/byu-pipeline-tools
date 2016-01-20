"""
department module
"""

class Department:
	"""
	Class describing departments that work on a project.
	"""

	DESIGN = "design"
	MODEL = "model"
	RIG = "rig"
	STORY = "story"
	LAYOUT = "layout"
	ANIM = "anim"
	MATERIAL = "material"
	CFX = "cfx"
	FX = "fx"
	LIGHTING = "lighting"
	COMP = "comp"
	FRONTEND = [DESIGN, MODEL, RIG, MATERIAL]
	BACKEND = [STORY, LAYOUT, ANIM, CFX, FX, LIGHTING, COMP]
	ALL = [DESIGN, MODEL, RIG, MATERIAL, STORY, LAYOUT, ANIM, CFX, FX, LIGHTING, COMP]