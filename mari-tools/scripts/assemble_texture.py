# Author: Ben DeMann

from byuam import Department, Project, Environment
from byugui.assemble_gui import AssembleWindow
from PySide import QtGui
import os
import mari

mari_assemble_dialog = None

def go():
	global mari_assemble_dialog
	parent = QtGui.QApplication.activeWindow()
	mari_assemble_dialog = AssembleWindow(parent, [Department.TEXTURE])
	mari_assemble_dialog.finished.connect(post_assemble)

def post_assemble():
	mari.projects.close()
	asset_name = mari_assemble_dialog.result
	print asset_name

	if asset_name is None:
		return

	# Set up the project and environment
	project = Project()
	environment = Environment()
	# get the username and asset
	username = project.get_current_username()
	asset = project.get_asset(asset_name)

	# get the texture element and check it out
	texture = asset.get_element(Department.TEXTURE)
	checkout_file = texture.checkout(username)

	# Get the path to the directory with all of the alembics
	model = asset.get_element(Department.MODEL)
	cache = model.get_cache_dir()

	geo_files = [x for x in os.listdir(model.get_cache_dir()) if not os.path.isdir(x)]
	# Remove anything that is not an alemibic file
	for file_path in list(geo_files):
		if(not str(file_path).lower().endswith('.abc')):
			geo_files.remove(file_path)

	geo_file_path = os.path.join(cache, geo_files[0])
	mari.projects.create(texture.get_long_name(), geo_file_path ,[],[],dict())

	for i in range(1, len(geo_files)):
		geo_file_path = os.path.join(cache, geo_files[i])
		mari.geo.load(geo_file_path)
		print "Loaded " + geo_file_path

	if True:
		return
