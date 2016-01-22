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

def mkdir(dirpath):
	"""
	create the given filepath. returns true if successful, false otherwise.
	"""
	try:
		os.mkdir(dirpath) # TODO: ensure correct permissions
	except OSError:
		return False # file already exists
	return True

def version_file(filepath, zero_pad=3):
	"""
	versions up the given file based on other files in the same directory. The given filepath 
	should not have a version at the end. e.g. given "/tmp/file.txt" this function will return 
	"/tmp/file_000.txt" unless there is already a file_000.txt in /tmp, in which case it will 
	return "/tmp/file_001.txt". zero_pad specifies how many digits to include in the version 
	number--the default is 3.
	"""
	raise NotImplementedError() # TODO