import json
import os

def readfile(filepath):
	"""
	reads a pipeline json file and returns the resulting dictionary
	"""
	with open(filepath, "r") as json_file:
		json_data = json.load(json_file)

	return json_data

def writefile(filepath, datadict):
	"""
	writes the given data dictionary to a pipeline json file at the given filepath
	"""
	with open(filepath, "w") as json_file:
		json.dump(datadict, json_file)

def mkdir(filepath):
	"""
	create the given filepath. returns true if successful, false otherwise.
	"""
	try:
		os.mkdir(filepath) # TODO: ensure correct permissions
	except OSError:
		return False # file already exists
	return True
