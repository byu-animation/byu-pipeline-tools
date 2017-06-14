from byuam import Department, Project, Environment
from byugui.assemble_gui import AssembleWindow
import os
import subprocess
import mari

def go():
	exportTex()

def exportTex():
	asset_name = None
	if asset_name is None:
		asset_name = "brennan"
		#TODO : Get the asset_name from the file name or from the assemble window
	exportImage(mari.geo.current(), asset_name, uvIndexList)
	print "Export Texture"

def makeTex(tif, tex):
	txmake = "txmake " + tif + " " + tex
	subprocess.Popen(txmake)

def exportImage(geo, asset_name):
	# Set up the project and environment
	project = Project()
	environment = Environment()
	# get the username and asset
	username = project.get_current_username()
	asset = project.get_asset(asset_name)

	# get the texture element and check it out
	texture = asset.get_element(Department.TEXTURE)

	baseDir = "/users/animation/bdemann/Desktop/mariTest/"
	# TODO : Figure out how to export the channel and not just the images from the channel
	channels = geo.channelList()
	for channel in channels:
		layers = channel.layerList()

		# find out which uv indices are being used in the channel
		# record them so we can keep track of their output files
		uvIndexList = set()
		for layer in layers:
			uvIndices = layer.inageSet().uvIndices()
			for uvIndex in uvIndices:
				uvIndexList.add(unIndex)

		channel_name = channel.name()
		file_name = asset_name + "-" + channel_name + "$UDIM.tif"
		file_path = os.path.join(baseDir, file_name)
		channel.exportImagesFlattened(file_path, 0, uvIndexList, None)

		# find each exported file and convert it to a .tex file
		for i in uvIndexList:
			udim = i + 1001
			file_name = asset_name + "-" channel_name + str(udim)
			old_file = file_name + ".tif"
			new_file = file_name + ".tex"
			old_file_path = os.path.join(baseDir, old_file)
			new_file_path = os.path.join(baseDir, old_file)
			makeTex(old_file_path, new_file_path)
