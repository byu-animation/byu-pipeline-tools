import pyqt_houdini
from TrHttpRPC import TrHttpRPC
import getpass
import urllib
import datetime
import os
import re
import shutil
import hou

# To be called from Houdini
def setUpGridmarkets():
	for node in hou.node("/obj").children():
		if node.name() != "ipr_camera":
			prepNodeForGridmarkets(node)
	for node in hou.node("/out").children():
		FixFilePaths()


# Recursively allow editing of contents on every node and it's children
def prepNodeForGridmarkets(node):
	node.allowEditingOfContents()
	# Dive in deeper and recursively do the same
	for child in node.children():
		prepNodeForGridmarkets(child)
	return

def changeFilePaths(node):
	if node.type().name() == "dusk_cameras":
		changePaths(node.parm('vm_picture'), "$JOB/render/ten_$F3.exr")
		changePaths(node.parm('vm_picture2'), "$JOB/render/jampa_$F3.exr")
		changePaths(node.parm('vm_picture3'), "$JOB/render/foreground_$F3.exr")
		changePaths(node.parm('vm_picture4'), "$JOB/render/gold_$F3.exr")
		changePaths(node.parm('vm_picture5'), "$JOB/render/background_$F3.exr")
		changePaths(node.parm('vm_picture6'), "$JOB/render/props_$F3.exr")
		changePaths(node.parm('vm_picture7'), "$JOB/render/effects_$F3.exr")
		changePaths(node.parm('vm_picture8'), "$JOB/render/shadow_$F3.exr")

def FixFilePaths():
	for node in hou.node("/out").children():
		if node.type().name() == "dusk_cameras":
			changePaths(node.parm('vm_picture'), '$JOB/production/shots/`chs("shot")`/render/`chs("version")`/ten_$F3.exr')
			changePaths(node.parm('vm_picture2'), '$JOB/production/shots/`chs("shot")`/render/`chs("version")`/jampa_$F3.exr')
			changePaths(node.parm('vm_picture3'), '$JOB/production/shots/`chs("shot")`/render/`chs("version")`/foreground_$F3.exr')
			changePaths(node.parm('vm_picture4'), '$JOB/production/shots/`chs("shot")`/render/`chs("version")`/gold_$F3.exr')
			changePaths(node.parm('vm_picture5'), '$JOB/production/shots/`chs("shot")`/render/`chs("version")`/background_$F3.exr')
			changePaths(node.parm('vm_picture6'), '$JOB/production/shots/`chs("shot")`/render/`chs("version")`/props_$F3.exr')
			changePaths(node.parm('vm_picture7'), '$JOB/production/shots/`chs("shot")`/render/`chs("version")`/effects_$F3.exr')
			changePaths(node.parm('vm_picture8'), '$JOB/production/shots/`chs("shot")`/render/`chs("version")`/shadow_$F3.exr')

def changePaths(parm, path):
	parm.lock(0)
	parm.set(path)
	parm.lock(1)
