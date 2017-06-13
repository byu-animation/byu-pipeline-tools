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

	project = Project()
	environment = Environment()
	username = project.get_current_username()
	asset = project.get_asset(asset_name)

	texture = asset.get_element(Department.TEXTURE)
	checkout_file = texture.checkout(username)

	# Get the path to the directory with all of the alembics
	element = asset.get_element(Department.MODEL)
	cache = element.get_cache_dir()

	# TODO: only load files whose extension matches element.get_cache_ext()
	geo_files = [x for x in os.listdir(element.get_cache_dir()) if not os.path.isdir(x)]

	geo = geo_files[0]
	mari.projects.create("testmultiple", geo ,[],[],dict())

	for geo_file in geo_files:
		mari.geo.load("/users/animation/bdemann/Documents/grendel-dev/production/assets/ben/model/main/cache/psphere1.abc")

	if True:
		return
