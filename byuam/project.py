import os
import shutil

from .body import Body, Asset, Shot
# from .department import Department
from .element import Checkout, Element
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

	def get_body(self, name):
		"""
		returns the body object associated with the given name.
		name -- the name of the body
		"""
		body = self.get_shot(name)
		if body is None:
			body = self.get_asset(name)
		return body

	def _create_body(self, name, bodyobj):
		name = pipeline_io.alphanumeric(name)
		filepath = os.path.join(bodyobj.get_parent_dir(), name)
		if name in self.list_bodies():
			raise EnvironmentError("body already exists: "+filepath)
		if not pipeline_io.mkdir(filepath):
			raise OSError("couldn't create body directory: "+filepath)
		datadict = bodyobj.create_new_dict(name)
		pipeline_io.writefile(os.path.join(filepath, bodyobj.PIPELINE_FILENAME), datadict)
		new_body = bodyobj(filepath)
		for dept in bodyobj.default_departments():
			pipeline_io.mkdir(os.path.join(filepath, dept))
			new_body.create_element(dept, Element.DEFAULT_NAME)
		return new_body

	def create_asset(self, name):
		"""
		creates a new shot with the given name, and returns the resulting shot object.
		If a shot with that name already exists, raises EnvironmentError.
		name -- the name of the new shot to create
		"""
		return self._create_body(name, Asset)

	def create_shot(self, name):
		"""
		creates a new shot with the given name, and returns the resulting shot object.
		If a shot with that name already exists, raises EnvironmentError.
		name -- the name of the new shot to create
		"""
		return self._create_body(name, Shot)

	def _list_bodies_in_dir(self, filepath, filter=None):
		dirlist = os.listdir(filepath)
		bodylist = []
		for bodydir in dirlist:
			abspath = os.path.join(filepath, bodydir)
			if os.path.exists(os.path.join(abspath, Body.PIPELINE_FILENAME)):
				bodylist.append(bodydir)
		bodylist.sort()
		if filter is not None and len(filter)==3:
			filtered_bodylist = []
			for body in bodylist:
				bodyobj = self.get_body(body)
				if bodyobj.has_relation(filter[0], filter[1], filter[2]):
					filtered_bodylist.append(body)
			bodylist = filtered_bodylist
		return bodylist

	def list_assets(self, filter=None):
		"""
		returns a list of strings containing the names of all assets in this project
		filter -- a tuple containing an attribute (string) relation (operator) and value 
		          e.g. (Asset.TYPE, operator.eq, AssetType.CHARACTER). Only returns assets whose
		          given attribute has the relation to the given desired value. Defaults to None.
		"""
		return self._list_bodies_in_dir(self._env.get_assets_dir(), filter)

	def list_shots(self, filter=None):
		"""
		returns a list of strings containing the names of all shots in this project
		filter -- a tuple containing an attribute (string) relation (operator) and value 
		          e.g. (Shot.FRAME)RANGE, operator.gt, 100). Only returns shots whose
		          given attribute has the relation to the given desired value. Defaults to None.
		"""
		return self._list_bodies_in_dir(self._env.get_shots_dir(), filter)

	def list_bodies(self):
		"""
		returns a list of strings containing the names of all bodies (assets and shots)
		"""
		return self.list_assets() + self.list_shots()

	def is_checkout_dir(self, path):
		"""
		returns True if the given path is a valid checkout directory
		returns False otherwise
		"""
		return os.path.exists(os.path.join(path, Checkout.PIPELINE_FILENAME))

	def get_checkout(self, path):
		"""
		returns the Checkout object describing the checkout operation at the given path
		If the path is not a valid checkout directory, returns None
		"""
		if not self.is_checkout_dir(path):
			return None
		return Checkout(path)

	def delete_shot(self, shot):
		"""
		delete the given shot
		"""
		if shot in self.list_shots():
			shutil.rmtree(os.path.join(self.get_shots_dir(), shot))

	def delete_asset(self, asset):
		"""
		delete the given asset
		"""
		if asset in self.list_assets():
			shutil.rmtree(os.path.join(self.get_asset_dir(), asset))
