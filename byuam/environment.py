import os

from . import pipeline_io

class Environment:

	PROJECT_ENV = "BYU_PROJECT_DIR"
	PIPELINE_FILENAME = ".project"

	PROJECT_NAME = "name"
	PRODUCTION_DIR = "production_dir"
	ASSETS_DIR = "assets_dir"
	SHOTS_DIR = "shots_dir"
	USERS_DIR = "users_dir"

	def __init__(self):
		"""
		Creates an Environment instance from data in the .project file in the directory defined by the 
		environment variable $BYU_PROJECT_DIR. If this variable is not defined or the .project file does
		not exist inside it, an EnvironmentError is raised.
		"""
		self._project_dir = os.getenv(Environment.PROJECT_ENV)
		if self._project_dir is None:
			raise EnvironmentError(Environment.PROJECT_ENV + " is not defined")
		
		project_file = os.path.join(self._project_dir, Environment.PIPELINE_FILENAME)
		if not os.path.exists(project_file):
			raise EnvironmentError(project_file + " does not exist")
		self._datadict = pipeline_io.readfile(project_file)

	def get_project_name(self):
		"""
		return the name of the current project
		"""
		return self._datadict[Environment.PROJECT_NAME]

	def get_project_dir(self):
		"""
		return the absolute filepath to the directory of the current project
		"""
		return os.path.abspath(self._project_dir)

	def get_assets_dir(self):
		"""
		return the absolute filepath to the assets directory of the current project
		"""
		return os.path.abspath(self._datadict[Environment.ASSETS_DIR])

	def get_shots_dir(self):
		"""
		return the absolute filepath to the shots directory of the current project
		"""
		return os.path.abspath(self._datadict[Environment.SHOTS_DIR])

	def get_users_dir(self):
		"""
		return the absolute filepath to the users directory of the current project
		"""
		return os.path.abspath(self._datadict[Environment.USERS_DIR])


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


class Status:
	"""
	Class describing status levels for elements.
	"""

	WAIT = "wait"
	READY = "ready"
	STARTED = "started"
	DONE = "done"
	ALL = [WAIT, READY, STARTED, DONE]

	def get_level(name):
		"""
		given a status name return the equivalent level
		e.g. WAIT    -> 0
			 READY   -> 1
			 STARTED -> 2
			 DONE    -> 3
		"""
		return Status.ALL.index(status)

	def get_name(level):
		"""
		given a status level return the equivalent name
		"""
		return Status.ALL[level]


class AssetType:
	"""
	Class describing types of assets.
	"""

	CHAR = "char"
	SET = "set"
	PROP = "prop"

