import hou
import os
from byuam import Project

def matchDefinition(node):
	filePath = node.type().definition().libraryFilePath()
	checkoutDir = os.path.split(filePath)[0]

	proj = Project()

	if not proj.is_checkout_dir(checkoutDir):
		node.matchCurrentDefinition()
		return

	element = proj.get_checkout_element(checkoutDir)
	hdaFile = element.get_long_name() + element.get_app_ext()
	productionElementPath = os.path.join(element.get_dir(), hdaFile)

	hou.hda.installFile(productionElementPath)
	hou.hda.uninstallFile(filePath)
	node.matchCurrentDefinition()
