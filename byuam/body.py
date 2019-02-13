import os

# from .department import Department
from .element import Element
from .environment import Department, Environment
from . import pipeline_io
from .registry import Registry

'''
body module
'''

class Body:
	'''
	Abstract class describing bodies that make up a project.
	'''
	# TODO allow users to subscribe to a body and recieve emails when changes are made
	PIPELINE_FILENAME = '.body'

	NAME = 'name'
	REFERENCES = 'references'
	DESCRIPTION = 'description'

	@staticmethod
	def create_new_dict(name):
		'''
		populate a dictionary with all the fields needed to create a new body
		'''
		datadict = {}
		datadict[Body.NAME] = name
		datadict[Body.REFERENCES] = []
		datadict[Body.DESCRIPTION] = ''
		return datadict

	@staticmethod
	def default_departments():
		'''
		return a list of departments that this body should create on initialization
		'''
		raise NotImplementedError('subclass must implement default_departments')

	@staticmethod
	def get_parent_dir():
		'''
		return the parent directory that bodies of this type are stored in
		'''
		raise NotImplementedError('subclass must implement get_parent_dir')

	def __init__(self, filepath):
		'''
		creates a Body instance describing the asset or shot stored in the given filepath
		'''
		self._env = Environment()
		self._filepath = filepath
		self._pipeline_file = os.path.join(filepath, Body.PIPELINE_FILENAME)
		if not os.path.exists(self._pipeline_file):
			raise EnvironmentError('not a valid body: ' + self._pipeline_file + ' does not exist')
		self._datadict = pipeline_io.readfile(self._pipeline_file)

	def get_name(self):

		return self._datadict[Body.NAME]

	def is_shot(self):

		raise NotImplementedError('subclass must implement is_shot')

	def is_asset(self):

		raise NotImplementedError('subclass must implement is_asset')

	def is_tool(self):

		raise NotImplementedError('subclass must implemtn is_tool')

	def is_crowd_cycle(self):

		raise NotImplementedError('subclass must implemtn is_crowd_cycle')

	def get_description(self):

		return self._datadict[Body.DESCRIPTION]

	# def get_parent_dir(self):
	# 	'''
	# 	return the parent directory that bodies of this type are stored in
	# 	'''
	# 	raise NotImplementedError('subclass must implement get_parent_dir')

	def get_element(self, department, name=Element.DEFAULT_NAME, force_create=False):
		'''
		get the element object for this body from the given department. Raises EnvironmentError
		if no such element exists.
		department -- the department to get the element from
		name -- the name of the element to get. Defaults to the name of the
				element created by default for each department.
		'''
		element_dir = os.path.join(self._filepath, department, name)
		if not os.path.exists(element_dir):
			if force_create:
				try:
					self.create_element(department, name)
				except Exception as e:
					print(e)
			else:
				raise EnvironmentError('no such element: ' + element_dir + ' does not exist')

		return Registry().create_element(department, element_dir)

	def create_element(self, department, name):
		'''
		create an element for this body from the given department and return the
		resulting element object. Raises EnvironmentError if the element already exists.
		department -- the department to create the element for
		name -- the name of the element to create
		'''
		dept_dir = os.path.join(self._filepath, department)
		if not os.path.exists(dept_dir):
			pipeline_io.mkdir(dept_dir)
		name = pipeline_io.alphanumeric(name)
		element_dir = os.path.join(dept_dir, name)
		if not pipeline_io.mkdir(element_dir):
			raise EnvironmentError('element already exists: ' + element_dir)
		empty_element = Registry().create_element(department)
		datadict = empty_element.create_new_dict(name, department, self.get_name())
		pipeline_io.writefile(os.path.join(element_dir, empty_element.PIPELINE_FILENAME), datadict)
		return Registry().create_element(department, element_dir)

	def list_elements(self, department):
		'''
		return a list of all elements for the given department in this body
		'''
		subdir = os.path.join(self._filepath, department)
		if not os.path.exists(subdir):
			return []
		dirlist = os.listdir(subdir)
		elementlist = []
		for elementdir in dirlist:
			abspath = os.path.join(subdir, elementdir)
			if os.path.exists(os.path.join(abspath, Element.PIPELINE_FILENAME)):
				elementlist.append(elementdir)
		elementlist.sort()
		return elementlist

	def add_reference(self, reference):
		'''
		Add the given reference to this body. If it already exists, do nothing. If reference is not a valid
		body, raise an EnvironmentError.
		'''
		ref_asset_path = os.path.join(self._env.get_assets_dir(), reference, Body.PIPELINE_FILENAME)
		ref_shot_path = os.path.join(self._env.get_shots_dir(), reference, Body.PIPELINE_FILENAME)
		ref_crowd_path = os.path.join(self._env.get_crowds_dir(), reference, Body.PIPELINE_FILENAME)
		if not os.path.exists(ref_asset_path) and not os.path.exists(ref_shot_path) and not os.path.exists(ref_crowd_path):
			raise EnvironmentError(reference + ' is not a valid body')
		if reference not in self._datadict[Body.REFERENCES]:
			self._datadict[Body.REFERENCES].append(reference)
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def remove_reference(self, reference):
		'''
		Remove the given reference, if it exists, and return True. Otherwise do nothing, and return False.
		'''
		try:
			self._datadict[Body.REFERENCES].remove(reference)
			return True
		except ValueError:
			return False
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def update_description(self, description):

		self._datadict[Body.DESCRIPTION] = description
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def get_references(self):
		'''
		Return a list of all references for this body.
		'''
		return self._datadict[Body.REFERENCES]

	def has_relation(self, attribute, relate, value):
		'''
		Return True if this body has the given attribute and if the given relationship
		to the the given value. Return False otherwise
		'''
		if attribute not in self._datadict:
			return False
		return relate(self._datadict[attribute],value)

class AssetType:
	'''
	Class describing types of assets.
	'''

	CHARACTER = 'character'
	SET = 'set'
	PROP = 'prop'
	ALL = [CHARACTER, SET, PROP]

class Asset(Body):
	'''
	Class describing an asset body.
	'''

	TYPE = 'type'

	@staticmethod
	def create_new_dict(name):

		datadict = Body.create_new_dict(name)
		datadict[Asset.TYPE] = AssetType.PROP
		return datadict

	@staticmethod
	def default_departments():

		return Department.ASSET_DEPTS

	@staticmethod
	def get_parent_dir():

		return Environment().get_assets_dir()

	def is_shot(self):

		return False

	def is_asset(self):

		return True

	def is_tool(self):

		return False

	def is_crowd_cycle(self):

		return False

	def get_type(self):

		return self._datadict[Asset.TYPE]

	def update_type(self, new_type):

		self._datadict[Asset.TYPE] = new_type
		pipeline_io.writefile(self._pipeline_file, self._datadict)

'''
shot module
'''

class Shot(Body):
	'''
	Class describing a shot body.
	'''
	FRAME_RANGE = 'frame_range'

	@staticmethod
	def create_new_dict(name):

		datadict = Body.create_new_dict(name)
		datadict[Shot.FRAME_RANGE] = 0
		return datadict

	@staticmethod
	def default_departments():

		return Department.SHOT_DEPTS

	@staticmethod
	def get_parent_dir():

		return Environment().get_shots_dir()

	def is_shot(self):

		return True

	def is_asset(self):

		return False

	def is_tool(self):

		return False

	def is_crowd_cycle(self):

		return False

	def get_frame_range(self):

		return self._datadict[Shot.FRAME_RANGE]

	def update_frame_range(self, frame_range):

		self._datadict[Shot.FRAME_RANGE] = frame_range
		pipeline_io.writefile(self._pipeline_file, self._datadict)

class Tool(Body):
	'''
	Class describing a tool body.
	'''

	@staticmethod
	def create_new_dict(name):

		datadict = Body.create_new_dict(name)
		return datadict

	@staticmethod
	def default_departments():

		return Department.TOOL_DEPTS

	@staticmethod
	def get_parent_dir():

		return Environment().get_tools_dir()

	def is_shot(self):

		return False

	def is_asset(self):

		return False

	def is_tool(self):

		return True

	def is_crowd_cycle(self):

		return False

class CrowdCycle(Body):
	'''
	Class describing a tool body.
	'''

	@staticmethod
	def create_new_dict(name):

		datadict = Body.create_new_dict(name)
		return datadict

	@staticmethod
	def default_departments():

		return Department.CROWD_DEPTS

	@staticmethod
	def get_parent_dir():

		return Environment().get_crowds_dir()

	def is_shot(self):

		return False

	def is_asset(self):

		return False

	def is_tool(self):

		return False

	def is_crowd_cycle(self):

		return True
