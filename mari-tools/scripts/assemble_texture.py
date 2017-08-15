# Author: Ben DeMann

from byuam import Department, Project, Environment
from byugui.assemble_gui import AssembleWindow, error_gui
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

	if len(geo_files) > 1:
		result = error_gui.light_error("There are multiple alembic files in " + str(file_path) + " and there should only be one.\nWould you like to continue anyways?\nIt might not work.")
		if not result:
			return
	elif len(geo_files) > 1:
		error_gui.error("There was no geo to bring it. Make sure that the model has been published in Maya.")

	geo_file_path = os.path.join(cache, geo_files[0])
	mari.projects.create(texture.get_long_name(), geo_file_path ,[],[],dict(), [{"/":mari.geo.GEOMETRY_IMPORT_DONT_MERGE_CHILDREN}, ])

	# At this point there should be no files left to add but if there are then the user was warned about it and we can go ahead and try to load those in.
	# This was from when we exported a bunch of alembics from Maya instead of just one. And since it shouldn't get called unless something goes wrong I figure it might be interesting to see what would happen if something goes wrong so we might as well leave it.
	for i in range(1, len(geo_files)):
		geo_file_path = os.path.join(cache, geo_files[i])
		mari.geo.load(geo_file_path)
		print "Loaded " + geo_file_path
