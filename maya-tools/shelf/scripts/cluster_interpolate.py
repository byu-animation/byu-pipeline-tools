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


def getVertList(vert1, vert2):
	currentSelection = pm.ls(selection=True)
	pm.select(pm.polySelectSp(vert1, vert2, q=True, loop=True))
	edge = pm.ls(selection=True)[0]
	pm.select(currentSelection)
	return edge
	#return pm.polySelectSp(vert1, vert2, q=True, loop=True)

def getClusterList(vertList):
	result = []

	allClusters = pm.ls(type="cluster") # O(1)

	for index, c in enumerate(allClusters): # O(c)
		objectSets = c.listConnections(type="objectSet") # O(1)

		print "this is the " + str(index) + "th cluster we are looking at"

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

		# TODO make sure that the object set is actually part of the geo.
		# TODO will we ever have a cluster that spans multiple geometries?
		# TODO will we ever be working with edges that go over multiple geometries? If we do then the vertList[1].node().getParent() will have a different parent.
		#hashSize = vertList.node().getParent().numVertices()
		vertSet = makeReadable(objectSet) #O(v)

		if contains(vertSet, vertList): # O(v)
			result.append(c) #O(1)
	return result

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

def contains(vertSet, vertList): # O(v)
	for vert in vertList: #O(v)
		if vert.currentItemIndex() in vertSet: # O(1)  if all of the vertexs are in an object hash add it to list. One vert that isn't in a set move on.
			return False
	return True

def makeReadable(objectSet): #O(v)
	# Worts case one there is a list of all the the points so c is v and the other is one c with all of the v so then it is still v so its just v. Well I mean its not that simple because of multiplication. But the idea is that it wont ever be quite v^2 I think

	# What a silly idea to use an array. Let's try a dictionary instead. What a silly idea to use a dictionary lets use a set instead.
	# objectHash = array('b', [False for i in range(hashSize)])
	# objectHash = {}
	vertSet = set()
	for e in objectSet: # O(n - v)
		# TODO if you get an object list then you can iterate over it to get a mesh vertex range and if you iterate over that you get a single mesh vertex but I don't know how to get the number from the mesh vertex
		for vert in e: # 0(v - n)
			vertSet.add(vert.currentItemIndex())
	return vertSet

def maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

def computeEdgeLengths(vertList, axis):
	edgeLen = array('f', [0 for vert in vertList])

	vertNums = vertList.indices()

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
		vertAName = str(vertList.node()) + ".vtx[" + str(vertNumA) + "]"
		vertBName = str(vertList.node()) + ".vtx[" + str(vertNumB) + "]"
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
			val1 = pm.percent(str(clust), str(self.vert1), v=True, q=True)[0]
			val2 = pm.percent(str(clust), str(self.vert2), v=True, q=True)[0]

		for i, vert in enumerate(vertList):
			if "Point Number" == self.interpolationAxis.getValue():
				percent = i / float((len(vertList) - 1))
			else:
				percent = edgeLengths[i]
			ratio = function(self.functionMenu.getValue(), percent)
			value = val1 * compliment(ratio) + val2 * ratio
			pm.percent(clust, vert, v=value)

	def create_layout(self):
		self.win = pm.window(title="Cluster Weight Interpolation")
		layout = pm.rowColumnLayout(numberOfColumns=2, columnAttach=(1, 'right', 0), columnWidth=[(1,100), (2, 250)], rowOffset=(6, "bottom", 15), rowSpacing=(1, 10), columnSpacing=(2,15))
		#chkBox = pm.checkBox(label = "My Checkbox", value=True, parent=layout)

		#Set up weight inputs
		pm.text(label="Min Weight")
		self.minWeight = pm.textField()
		pm.text(label="Max Weight")
		self.maxWeight = pm.textField()

		#Set up cluster Menu
		pm.text(label='Cluster')
		self.clusterMenu = pm.optionMenu()
		clusterList = getClusterList(self.vertList)
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

		#Set up Axis Menu
		pm.text(label='Axies')
		self.interpolationAxis = pm.optionMenu()
		print "This is the type of the menu so that we can get the stuff from it"
		print type(self.interpolationAxis)
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
