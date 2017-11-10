import nuke
import os
from byuam import Project

def go():
	print "Start copy"
	project = Project()
	proDir = project.get_project_dir()
	path = os.path.join(proDir, 'byu-pipeline-tools', 'nuke-tools', 'templates', 'grendel_general_template.nk')
	print path
	nuke.nodePaste(path)
	print "Finsih Copy"
