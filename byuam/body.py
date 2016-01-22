import os

from .department import Department
from .element import Element
from .environment import Environment
from . import pipeline_io
from .registry import Registry

"""
body module
"""

class Body:
	"""
	Abstract class describing bodies that make up a project.
	"""
	# TODO allow users to subscribe to a body and recieve emails when changes are made
	# TODO allow more than one element per department to be created
	PIPELINE_FILENAME = ".body"

	NAME = 'name'
	
	@staticmethod
	def create_new_dict(name):
		"""
		populate a dictionary with all the fields needed to create a new body
		"""
		datadict = {}
		datadict[Body.NAME] = name
		return datadict

	def __init__(self, filepath):
		"""
		creates a Body instance describing the asset or shot stored in the given filepath
		"""
		self._env = Environment()
		self._filepath = filepath
		self._pipeline_file = os.path.join(filepath, Body.PIPELINE_FILENAME)
		if not os.path.exists(self._pipeline_file):
			raise EnvironmentError("not a valid body: " + self._pipeline_file + " does not exist")
		self._datadict = pipeline_io.readfile(self._pipeline_file)

	def get_name(self):

		return self._datadict[Body.NAME]

	def get_parent_dir(self):
		"""
		return the parent directory that bodies of this type are stored in
		"""
		raise NotImplementedError('subclass must implement get_parent_dir')

	def get_element(self, department, name="main"):
		"""
		get the element object for this body from the given department. Raises EnvironmentError 
		if no such element exists.
		department -- the department to get the element from
		name -- the name of the element to get. Defaults to "main" which is the name of the
				element created by default for each department.
		"""
		element_dir = os.path.join(self._filepath, department, name)
		if not os.path.exists(element_dir):
			raise EnvironmentError(element_dir + " does not exist")

		return Registry().create_element(department, element_dir)

	def create_element(self, department, name):
		"""
		create an element for this body from the given department and return
		the resulting element object. Returns None if the element already exists.
		department -- the department to create the element for
		name -- the name of the element to create
		"""
		element_dir = os.path.join(self._filepath, department, name)
		if not pipeline_io.mkdir(element_dir):
			return None
		empty_element = Registry().create_element(department)
		datadict = empty_element.create_new_dict(name, department, self.get_name())
		pipeline_io.writefile(os.path.join(element_dir, empty_element.PIPELINE_FILENAME), datadict)
		return Registry().create_element(department, element_dir)


class Asset(Body):
	"""
	Class describing an asset body.
	"""

	TYPE = "type" 

	@staticmethod
	def create_new_dict(name):
		
		datadict = Body.create_new_dict(name)
		datadict[Asset.TYPE] = "CHAR"
		return datadict

	# TODO check valid asset names (alpha_numeric, etc)
	# TODO references to other assets ?

	def get_parent_dir(self):

		return self._env.get_assets_dir()

	def get_type(self):

		return self._datadict[Asset.TYPE] # TODO: asset type enumeration? e.g. PROP, SET, CHAR, etc.


from body import Body

"""
shot module
"""

class Shot(Body):
	"""
	Class describing a shot body.
	"""
	FRAME_RANGE = "frame_range"

	@staticmethod
	def create_new_dict(name):
		
		datadict = Body.create_new_dict(name)
		datadict[Shot.FRAME_RANGE] = 0
		return datadict

	# TODO check valid shot names (zero padded etc.)
	# TODO reference assets ?

	def get_parent_dir(self):

		return self._env.get_shots_dir()

	def get_frame_range(self):

		return self._datadict[Shot.FRAME_RANGE]

