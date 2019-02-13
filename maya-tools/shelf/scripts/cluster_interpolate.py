from PySide2 import QtWidgets
from PySide2.QtWidgets import *
import pymel.core as pm

from array import array
from byugui import message_gui

WINDOW_WIDTH = 250
WINDOW_HEIGHT = 100

def go():

	verts = pm.ls(selection=True)

	if len(verts) is not 2:
		message_gui.error("Please select two vertices to interpolate between")
		return

	vert1 = verts[0]
	vert2 = verts[1]

	if type(vert1) is not pm.general.MeshVertex or type(vert2) is not pm.general.MeshVertex:
		message_gui.error("Please select two vertices to interpolate between")

	dialog = ClusterInterpolationWindow(vert1, vert2)
	dialog.show()

def sortVertList(vert1, vert2, vertList):
	currentVert = vert1
	result = list()
	while currentVert != vert2:
		# print "This is the currentVert: ", currentVert
		connectedVerts = currentVert.connectedVertices()
		for vert in connectedVerts:
			if vert in vertList and vert not in result:
				result.append(vert)
				currentVert = vert
	return result

def getVertList(vert1, vert2):
	currentSelection = pm.ls(selection=True)
	loop = pm.polySelectSp(vert1, vert2, q=True, loop=True)
	pm.select(loop)
	# We want to do the select and ls steps because they give us a list of Mesh Vertieces in stead of list of strings
	edge = pm.ls(selection=True)
	edgeVerts = list()
	for vertMesh in edge:
		for vert in vertMesh:
			edgeVerts.append(vert)
	pm.select(currentSelection)
	return sortVertList(vert1, vert2, edgeVerts)

def getClusterListForVert(vert, clusters=None):
	result = []

	if clusters is None:
		clusters = pm.ls(type="cluster")

	clusterCnt = len(clusters)

	for index, c in enumerate(clusters):
		objectSets = c.listConnections(type="objectSet")

		if not len(objectSets) == 1:
			results = list()
			for objSet in objectSets:
				if "cluster" in objSet.name():
					results.append(objSet)
			if not len(results) == 1:
				message_gui.error("There is more than one object set tied to this cluster. That is something I didn't expect. Please let me know about it. Let's keep going though and see what happens. The list of object sets looks like this: " + str(results))
				continue
			else:
				objectSet = results[0]
		else:
			objectSet = objectSets[0]

		if vert in objectSet[0]:
			result.append(c)

		print str(index + 1) + " of " + str(clusterCnt) + " clusters processed."
	print "Len of result: ", len(result)
	print "Type of clusters: ", type(clusters[0])
	print "Type of result items: ", type(result[0])
	return result

def getClusterList(vertList, clusters=None, quick=False):
	if quick:
		quickVertList = list()
		quickVertList.append(vertList[0])
		endIndex = len(vertList) - 1
		quickVertList.append(vertList[endIndex])
		return getClusterList(quickVertList, clusters=clusters)
	for vert in vertList:
		clusters = getClusterListForVert(vert, clusters=clusters)
	return clusters

def allClustersOnVert(vert, clusters=None):
	'''
	Using the percent query we really quickly get all of the clusters that affect the geo for the given vert. This greatly reduces the number of clusters we have to process for scenes that have multriple pieces of geometry.
	'''
	if clusters is None:
		clusters = pm.ls(type="cluster")
		print len(clusters), " is the length of all the clusters. Should be about 300"
	result = list()
	for i, cluster in enumerate(clusters):
		vals = pm.percent(cluster, vert, v=True, q=True)
		if vals is not None:
			result.append(cluster)
			# print i, ": ", vals
	return result

def hybridClusterList(vertList):
	clusters = allClustersOnVert(vertList[0])
	clusters = getClusterList(vertList, clusters=clusters, quick=True)
	return clusters

def function(function, inputVal):
	if function == "Linear":
		return inputVal
	if function == "Quadratic":
		return inputVal * inputVal
	if function == "Ramp":
		return pm.gradientControlNoAttr( 'falloffCurve', q=True, vap=inputVal)
		raise Exception('Not implemented')
	else:
		raise Exception('Not a valid function')

def compliment(val):
	return abs(val - 1)

def maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

def computeEdgeLengths(vertList, axis):
	edgeLen = array('f', [0 for vert in vertList])

	vertNums = list()

	for vert in vertList:
		vertNums.append(vert.currentItemIndex())

	# We are going to go over each vertex and add the line length to a total to get the total length from that point to the first point in the array.
	# We can't do just the direct distance from point 0 to point i because if the geo loops around then there might be a shorter path to point 0 that doesn't go though all of the other points in the geo. So we need to step through and makes sure we measure all of the edges.
	# Once we have how far away point i is from point 0 we convert it to a percent of the total length from point 0 to point n and we return that list of percents
	for i, vertNumA in enumerate(vertNums):
		if i == 0:
			# First point is 0 away from the first point.
			edgeLen[0] = 0
			continue

		preVertNum = i - 1
		vertNumB = vertNums[preVertNum]
		vertAName = str(vertList[0].node()) + ".vtx[" + str(vertNumA) + "]"
		vertBName = str(vertList[0].node()) + ".vtx[" + str(vertNumB) + "]"
		vertA = pm.ls(vertAName)[0]
		vertB = pm.ls(vertBName)[0]
		posA = vertA.getPosition(space="world")
		posB = vertB.getPosition(space="world")
		vect = posA - posB

		if not "x" in axis:
			vect[0] = 0
		if not "y" in axis:
			vect[1] = 0
		if not "z" in axis:
			vect[2] = 0

		edgeLen[i] = edgeLen[i-1] + vect.length()

	totalLen = edgeLen[len(edgeLen)-1]
	for i, l in enumerate(edgeLen):
		if totalLen == 0:
			edgeLen[i] = 0
		else:
			edgeLen[i] /= totalLen
	return edgeLen

class ClusterInterpolationWindow():
	def __init__(self, vert1, vert2, parent=maya_main_window()):
		self.vert1 = vert1
		self.vert2 = vert2
		self.vertList = getVertList(vert1, vert2)
		self.create_layout()
		self.rampName = ""

	def interpolate(self):
		clust = pm.ls(self.clusterMenu.getValue())[0]
		vertList = self.vertList
		if not "Point Number" == self.interpolationAxis.getValue():
			edgeLengths = computeEdgeLengths(vertList, self.interpolationAxis.getValue())

		minWeight = self.minWeight.getText()
		maxWeight = self.maxWeight.getText()

		if not minWeight == "" and not maxWeight == "":
			val1 = float(minWeight)
			val2 = float(maxWeight)
		else:
			val1 = pm.percent(clust, self.vert1, v=True, q=True)[0]
			val2 = pm.percent(str(clust), str(self.vert2), v=True, q=True)[0]

		print "START INTERPOLATING THIS VERT LIST: " + str(vertList)
		isReversed = self.invert.getValue() == 'invert'
		if isReversed:
			temp = val1
			val1 = val2
			val2 = temp
			print"Here is the updated one"
		for i, vert in enumerate(vertList):
			print "We are working on the " + str(i) + "th vert in the list."
			if "Point Number" == self.interpolationAxis.getValue():
				percent = i / float((len(vertList) - 1))
			else:
				percent = edgeLengths[i]
			ratio = function(self.functionMenu.getValue(), percent)
			value = val1 * compliment(ratio) + val2 * ratio
			oldValue = pm.percent(str(clust), str(vert), v=True, q=True)
			print "vert " + str(vert) + " is getting the value " + str(value) + ". Old value was: " + str(oldValue)
			print "we are assigning it to this cluster: " + str(clust)
			pm.percent(clust, vert, v=value)
			actualValue = pm.percent(str(clust), str(vert), v=True, q=True)[0]
			print "actual value recieved: " + str(actualValue)
		print "FINSIH"
		print ""

	def create_layout(self):
		self.win = pm.window(title="Cluster Weight Interpolation")
		layout = pm.rowColumnLayout(numberOfColumns=2, columnAttach=(1, 'right', 0), columnWidth=[(1,150), (2, 250)], rowOffset=(6, "bottom", 15), rowSpacing=(1, 10), columnSpacing=(2,15))
		#chkBox = pm.checkBox(label = "My Checkbox", value=True, parent=layout)

		#Set up weight inputs
		pm.text(label="Min Weight")
		self.minWeight = pm.textField()
		pm.text(label="Max Weight")
		self.maxWeight = pm.textField()

		#Set up cluster Menu
		pm.text(label='Cluster')
		self.clusterMenu = pm.optionMenu()
		clusterList = hybridClusterList(self.vertList)
		for c in clusterList:
			pm.menuItem(label=str(c))

		#Set up Equation Menu
		pm.text(label='Equation')
		self.functionMenu = pm.optionMenu()
		pm.menuItem(label='Ramp')
		pm.menuItem(label='Linear')
		pm.menuItem(label='Quadratic')

		#Set up Ramp
		#TODO is there a way that we can hide or disable this thing if the user should select to use the Linear or Quadratic options?
		pm.text(label='Ramp Value')
		pm.optionVar(stringValueAppend=['falloffCurveOptionVar', '0,1,2'])
		pm.optionVar(stringValueAppend=['falloffCurveOptionVar', '1,0,2'])
		pm.gradientControlNoAttr( 'falloffCurve', h=90)
		self.ramp = pm.gradientControlNoAttr( 'falloffCurve', e=True, optionVar='falloffCurveOptionVar' )

		pm.text(label='Invert')
		self.invert = pm.optionMenu()
		pm.menuItem(label='Yes')
		pm.menuItem(label='No')

		#Set up Axis Menu
		pm.text(label='Axies for Dist Measurement')
		self.interpolationAxis = pm.optionMenu()
		pm.menuItem(label='xyz')
		pm.menuItem(label='x')
		pm.menuItem(label='y')
		pm.menuItem(label='z')
		pm.menuItem(label='xy')
		pm.menuItem(label='xz')
		pm.menuItem(label='yz')
		pm.menuItem(label='Point Number')

		#Set up Buttons
		closeBtn = pm.button(label="Close", parent=layout)
		interpolateBtn = pm.button(label="Interpolate", parent=layout)

		interpolateBtn.setCommand(lambda *args: self.interpolate())
		closeBtn.setCommand(lambda *args: self.close_dialog())

	def show(self):
		self.win.show()

	def close_dialog(self):
		self.win.delete()

if __name__ == '__main__':
	go()
