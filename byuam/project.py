import os

from .body import Body, Asset, Shot
# from .department import Department
from .element import Element
from .environment import Department, Environment
from . import pipeline_io
from .registry import Registry

class Project:
	"""
	Class describing an animation project.
	"""

	def __init__(self):
		"""
		creates a Project instance for the currently defined project from the environment
		"""
		self._env = Environment()
	def get_name(self):
		"""
		return the name of the this project
		"""
		return self._env.get_project_name()

	def get_project_dir(self):
		"""
		return the absolute filepath to the directory of this project
		"""
		return self._env.get_project_dir()

	def get_assets_dir(self):
		"""
		return the absolute filepath to the assets directory of this project
		"""
		return self._env.get_assets_dir()

	def get_shots_dir(self):
		"""
		return the absolute filepath to the shots directory of this project
		"""
		return self._env.get_shots_dir()

	def get_users_dir(self):
		"""
		return the absolute filepath to the users directory of this project
		"""
		return self._env.get_users_dir()

	def get_asset(self, name):
		"""
		returns the asset object associated with the given name.
		name -- the name of the asset
		"""
		filepath = os.path.join(self._env.get_assets_dir(), name)
		if not os.path.exists(filepath):
			return None
		return Asset(filepath)

	def get_shot(self, name):
		"""
		returns the shot object associated with the given name.
		name -- the name of the shot
		"""
		filepath = os.path.join(self._env.get_shots_dir(), name)
		if not os.path.exists(filepath):
			return None
		return Shot(filepath)

	def create_asset(self, name):
		"""
		creates a new shot with the given name, and returns the resulting shot object.
		If a shot with that name already exists, returns None.
		name -- the name of the new shot to create
		"""
		filepath = os.path.join(self._env.get_assets_dir(), name)
		if not pipeline_io.mkdir(filepath):
			return None
		datadict = Asset.create_new_dict(name)
		pipeline_io.writefile(os.path.join(filepath, Body.PIPELINE_FILENAME), datadict)
		new_asset = Asset(filepath)
		for dept in Department.FRONTEND:
			pipeline_io.mkdir(os.path.join(filepath, dept))
			new_asset.create_element(dept, Element.DEFAULT_NAME)
		return new_asset

	def create_shot(self, name):
		"""
		creates a new shot with the given name, and returns the resulting shot object.
		If a shot with that name already exists, returns None.
		name -- the name of the new shot to create
		"""
		filepath = os.path.join(self._env.get_shots_dir(), name)
		if not pipeline_io.mkdir(filepath):
			return None
		datadict = Shot.create_new_dict(name)
		pipeline_io.writefile(os.path.join(filepath, Body.PIPELINE_FILENAME), datadict)
		new_shot = Shot(filepath)
		for dept in Department.BACKEND:
			pipeline_io.mkdir(os.path.join(filepath, dept))
			new_shot.create_element(dept, Element.DEFAULT_NAME)
		return new_shot

	def _list_bodies(self, filepath):
		dirlist = os.listdir(filepath)
		assetlist = []
		for assetdir in dirlist:
			abspath = os.path.join(filepath, assetdir)
			if os.path.isdir(abspath) and os.path.exists(os.path.join(abspath, Body.PIPELINE_FILENAME)):
				assetlist.append(assetdir)
		assetlist.sort()
		return assetlist

	def list_assets(self):
		"""
		returns a list of strings containing the names of all assets in this project
		"""
		return self._list_bodies(self._env.get_assets_dir())

	def list_shots(self):
		"""
		returns a list of strings containing the names of all shots in this project
		"""
		return self._list_bodies(self._env.get_shots_dir())
