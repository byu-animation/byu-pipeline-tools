from byuam import Department, Project
from byugui.selection_gui import SelectionWindow
from PySide import QtGui
import os
import subprocess
import mari

ALL = "all"
SELECTED_GEO = "geo"
SELECTED_CHANNEL = "channel"
mari_selection_dialog = None

def go(scope = ALL):
	global mari_selection_dialog
	texture = get_texture()
	if texture is None:
		parent = QtGui.QApplication.activeWindow()
		mari_selection_dialog = SelectionWindow(parent, [Department.TEXTURE])
		if scope is SELECTED_GEO:
			mari_selection_dialog.finished.connect(export_selected_geo_to_tex)
		elif scope is SELECTED_CHANNEL:
			mari_selection_dialog.finished.connect(export_selected_channel_to_tex)
		else:
			mari_selection_dialog.finished.connect(export_all_to_tex)
	else:
		if scope is SELECTED_GEO:
			export_selected_geo_to_tex(texture)
		elif scope is SELECTED_CHANNEL:
			export_selected_channel_to_tex(texture)
		else:
			export_all_to_tex(texture)

def get_texture():
	project_name = mari.projects.current().name()
	index = project_name.find("_texture")
	if index > 0:
		asset_name = project_name[:index]
		project = Project()
		asset = project.get_asset(asset_name)
		return asset.get_element(Department.TEXTURE)
	else:
		return None

def export_selected_geo_to_tex(texture = None):
	if texture is None:
		texture = mari_selection_dialog.result
		if texture is None:
			return
	if not(texture.get_department() == Department.TEXTURE):
		print "Invalid element: Expecting " + str(Department.TEXTURE) + " and got " + str(texture.get_department())
		return
	geo = mari.geo.current()

	export_geo_to_tex(geo, texture)
	print "Exported tex file for selected geo"

def export_selected_channel_to_tex(texture = None):
	if texture is None:
		texture = mari_selection_dialog.result
		if texture is None:
			return
	if not(texture.get_department() == Department.TEXTURE):
		print "Invalid element: Expecting " + str(Department.TEXTURE) + " and got " + str(texture.get_department())
		return
	channel = mari.geo.current().currentChannel()

	export_channel_to_tex(channel, texture)
	print "Export tex file for selected Channel"

def export_all_to_tex(texture = None):
	if texture is None:
		texture = mari_selection_dialog.result
		if texture is None:
			return
	if not(texture.get_department() == Department.TEXTURE):
		print "Invalid element: Expecting " + str(Department.TEXTURE) + " and got " + str(texture.get_department())
		return

	geo_list = mari.geo.list()

	for geo in geo_list:
		export_geo_to_tex(geo, texture)
	print "Exported all Textures tex files"

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
	# get the layers from the channel
	layers = channel.layerList()

	# break up all the groups
	allLayers = list()
	while len(layers) > 0:
		temp_layers = list()
		for layer in list(layers):
			if layer.isPaintableLayer():
				allLayers.append(layer)
			elif layer.isGroupLayer():
				sublayers = layer.layerStack().layerList()
				temp_layers.extend(sublayers)
			layers.remove(layer)
		layers = temp_layers

	# count the uvIndices in each layer
	for layer in allLayers:
		if not layer.isPaintableLayer():
			continue
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

	if len(uvIndexList) < 1:
		print "There was a problem with the uvIndex list. It is emptyp"

	# find each exported file and convert it to a .tex file
	for i in uvIndexList:
		udim = i + 1001
		file_name = file_base + "-" + str(udim)
		old_file = file_name + ".tif"
		new_file = file_name + ".tex"
		old_file_path = os.path.join(baseDir, old_file)
		new_file_path = os.path.join(baseDir, new_file)
		makeTex(old_file_path, new_file_path)
