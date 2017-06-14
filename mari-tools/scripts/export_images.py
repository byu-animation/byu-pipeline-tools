from byuam import Department, Project
from byugui.assemble_gui import AssembleWindow
from PySide import QtGui
import os
import subprocess
import mari

ALL = "all"
SELECTED_GEO = "geo"
SELECTED_CHANNEL = "channel"
mari_assemble_dialog = None

def go(scope = ALL):
	global mari_assemble_dialog
	asset_name = get_asset_name()
	if asset_name is None:
		parent = QtGui.QApplication.activeWindow()
		mari_assemble_dialog = AssembleWindow(parent, [Department.TEXTURE])
		if scope is SELECTED_GEO:
			mari_assemble_dialog.finished.connect(export_selected_geo_to_tex)
		elif scope is SELECTED_CHANNEL:
			mari_assemble_dialog.finished.connect(export_selected_channel_to_tex)
		else:
			mari_assemble_dialog.finished.connect(export_all_to_tex)
	else:
		if scope is SELECTED_GEO:
			export_selected_geo_to_tex(asset_name)
		elif scope is SELECTED_CHANNEL:
			export_selected_channel_to_tex(asset_name)
		else:
			export_all_to_tex(asset_name)

def get_asset_name():
	project_name = mari.projects.current().name()
	index = project_name.find("_texture")
	if index > 0:
		return project_name[:index]
	else:
		return None

def get_texture(asset_name):
	# Set up the project
	project = Project()
	# get asset body
	asset = project.get_asset(asset_name)
	# return the texture element
	return asset.get_element(Department.TEXTURE)

def export_selected_geo_to_tex(asset_name = None):
	texture = get_texture(get_asset_name())
	geo = mari.geo.current()

	export_geo_to_tex(geo, texture)
	print "Exported .tex for selected geo"

def export_selected_channel_to_tex(asset_name = None):
	texture = get_texture(get_asset_name())
	channel = mari.geo.current().currentChannel()

	export_channel_to_tex(channel, texture)
	print "Export for selected Channel"

def export_all_to_tex(asset_name = None):
	if asset_name is None:
		asset_name = mari_assemble_dialog.result
		if asset_name is None:
			return

	texture = get_texture(asset_name)
	geo_list = mari.geo.list()

	for geo in geo_list:
		export_geo_to_tex(geo, texture)
	print "Export all Textures"

def makeTex(tif, tex):
	subprocess.call(["txmake", tif, tex])
	subprocess.call(["rm", tif])

def export_geo_to_tex(geo, texture):
	channels = geo.channelList()
	for channel in channels:
		export_channel_to_tex(channel, texture)

def export_channel_to_tex(channel, texture):
	# get cache directory so we can save the textures there
	baseDir = texture.get_cache_dir()

	# find out which uv indices are being used in the channel
	# record them so we can keep track of their output files
	uvIndexList = set()
	# get the layers from the channel and cound the uvIndices in each layer
	layers = channel.layerList()
	for layer in layers:
		uvIndices = layer.imageSet().uvIndices()
		for uvIndex in uvIndices:
			uvIndexList.add(uvIndex)
	uvIndexList = list(uvIndexList)

	# build output paths for tif and tex
	channel_name = channel.name()
	geo_name = channel.geoEntity().name()
	file_base = texture.get_parent() + "-" +  texture.get_name() + "-" + geo_name + "-" + channel_name
	file_name = file_base + "-" + "$UDIM.tif"
	file_path = os.path.join(baseDir, file_name)
	channel.exportImagesFlattened(file_path, 0, uvIndexList, None)

	# find each exported file and convert it to a .tex file
	for i in uvIndexList:
		udim = i + 1001
		file_name = file_base + "-" + str(udim)
		old_file = file_name + ".tif"
		new_file = file_name + ".tex"
		old_file_path = os.path.join(baseDir, old_file)
		new_file_path = os.path.join(baseDir, new_file)
		makeTex(old_file_path, new_file_path)
