# Author: Ben DeMann
import hou

def go():
	obj = hou.node('obj')
	out = hou.node('out')

	ris = out.createNode('ris')

	dome = obj.createNode('pxrdomelight')
	dome.setParms({'lightColorMap':'$JOB/byu-pipeline-tools/assets/lights/default-hdr.tex'})
