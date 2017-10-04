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

	for c in allClusters: # O(c)
		objectSet = c.listConnections(type="objectSet") # O(1)

		if not len(objectSet) == 1:
			message_gui.error("There is more than one object set tied to this cluster. That is something I didn't expect. Please let me know about it. Let's keep going though and see what happens")
			continue
		else:
			objectSet = objectSet[0]

		# TODO make sure that the object set is actually part of the geo.
		# TODO will we ever have a cluster that spans multiple geometries?
		# TODO will we ever be working with edges that go over multiple geometries? If we do then the vertList[1].node().getParent() will have a different parent.
		hashSize = vertList.node().getParent().numVertices()
		objectHash = makeReadable(objectSet, hashSize) #O(v)

		if contains(objectHash, vertList): # O(v)
			result.append(c) #O(1)
	return result

def function(function, inputVal):
	if function == "Linear":
		return inputVal
	if function == "Quadratic":
		return inputVal * inputVal
	else:
		raise Exception('Not a valid function')

def compliment(val):
	return abs(val - 1)

def contains(objectHash, vertList): # O(v)
	for vert in vertList: #O(v)
		if objectHash[vert.currentItemIndex()] is 0: # O(1)  if all of the vertexs are in an object hash add it to list. One vert that isn't in a set move on.
			return False
	return True

def makeReadable(objectSet, hashSize): #O(v)
	# Worts case one there is a list of all the the points so c is v and the other is one c with all of the v so then it is still v so its just v. Well I mean its not that simple because of multiplication. But the idea is that it wont ever be quite v^2 I think
	objectHash = array('b', [False for i in range(hashSize)])
	for e in objectSet: # O(n - v)
		# TODO if you get an object list then you can iterate over it to get a mesh vertex range and if you iterate over that you get a single mesh vertex but I don't know how to get the number from the mesh vertex
		for vert in e: # 0(v - n)
			objectHash[vert.currentItemIndex()] = True # O(1)
	return objectHash

def maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

class ClusterInterpolationWindow(QDialog):
	def __init__(self, vert1, vert2, parent=maya_main_window()):
		QDialog.__init__(self, parent)
		self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
		self.vert1 = vert1
		self.vert2 = vert2
		self.vertList = getVertList(vert1, vert2)
		self.create_layout()

	def interpolate(self):
		clust = pm.ls(self.clusterMenu.currentText())[0]
		vertList = self.vertList

		input1 = self.input1.displayText()
		input2 = self.input2.displayText()

		if not input1 == "" and not input2 == "":
			val1 = float(input1)
			val2 = float(input2)
		else:
			val1 = pm.percent(str(clust), str(self.vert1), v=True, q=True)[0]
			val2 = pm.percent(str(clust), str(self.vert2), v=True, q=True)[0]

		for i, vert in enumerate(vertList):
			percentLocation = i / float((len(vertList) - 1))
			ratio = function(self.functionMenu.currentText(), percentLocation)
			value = val1 * compliment(ratio) + val2 * ratio
			pm.percent(clust, vert, v=value)

	def create_layout(self):
		self.input1 = QtWidgets.QLineEdit()
		self.input2 = QtWidgets.QLineEdit()

		self.clusterMenu = QtWidgets.QComboBox()
		clusterList = getClusterList(self.vertList)
		for c in clusterList:
			self.clusterMenu.addItem(str(c))

		self.functionMenu = QtWidgets.QComboBox()
		self.functionMenu.addItem("Linear")
		self.functionMenu.addItem("Quadratic")

		self.interpolateButton = QPushButton('Interpolate')
		self.interpolateButton.clicked.connect(self.interpolate)
		self.closeButton = QPushButton('Close')
		self.closeButton.clicked.connect(self.close_dialog)

		#Create button layout
		button_layout = QHBoxLayout()
		button_layout.setSpacing(2)
		button_layout.addStretch()

		button_layout.addWidget(self.interpolateButton)
		button_layout.addWidget(self.closeButton)

		#Create main layout
		main_layout = QVBoxLayout()
		main_layout.setSpacing(2)
		main_layout.setMargin(2)
		main_layout.addWidget(self.input1)
		main_layout.addWidget(self.input2)
		main_layout.addWidget(self.clusterMenu)
		main_layout.addWidget(self.functionMenu)
		main_layout.addLayout(button_layout)

		self.setLayout(main_layout)

	def close_dialog(self):
		self.close()

if __name__ == '__main__':
	go()
