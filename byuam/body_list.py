#Author: Edward Pingel

#class to load names of body catagories from text document
import json

class NameList:
	def __init__(self):
		categories = None
	def loadList(self, list_file_name):
		with open(list_file_name, 'r') as categories_file:
		    self.categories = json.load(categories_file)
		return self.categories

	def getNames(self):
		return self.categories
