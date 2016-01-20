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
		return self._project_dir

	def get_assets_dir(self):
		"""
		return the absolute filepath to the assets directory of the current project
		"""
		return self._datadict[Environment.ASSETS_DIR]

	def get_shots_dir(self):
		"""
		return the absolute filepath to the shots directory of the current project
		"""
		return self._datadict[Environment.SHOTS_DIR]

	def get_users_dir(self):
		"""
		return the absolute filepath to the users directory of the current project
		"""
		return self._datadict[Environment.USERS_DIR]