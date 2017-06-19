# Author: Ben DeMann
import hou

def go():
	obj = hou.node('obj')
	out = hou.node('out')
	shop = hou.node('shop')

	ris = out.createNode('ris')

	risnet = shop.createNode('risnet')
	risnet.createNode('pxrsurface')

	dome = obj.createNode('pxrdomelight')
	dome.setParms({'lightColorMap':'$JOB/byu-pipeline-tools/assets/lights/footprint-court.tex'})
