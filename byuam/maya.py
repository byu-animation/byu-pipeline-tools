from .element import Element

class MayaElement(Element):
	"""
	class describing elements created in Autodesk Maya
	"""

	@staticmethod
	def create_new_dict(name, department, parent_name):
		data_dict = Element.create_new_dict(name, department, parent_name)
		data_dict[Element.APP_EXT] = ".mb"
		return data_dict
