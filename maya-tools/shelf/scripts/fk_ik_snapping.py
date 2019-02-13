#Author: Ben DeMann

import maya.cmds as cmds
import numpy as np

def ik_to_fk_match(name, limb, side):

	if limb == 'arm':
		lower_joint = 'wrist'
	elif limb == 'leg':
		lower_joint = 'ankle'

	fkUpperJointName = name + '_' + side + '_upper_' + limb + '_FK_JNT_01'
	fkMiddleJointName = name + '_' + side + '_lower_' + limb + '_FK_JNT_01'
	fkLowerJointName = name + '_' + side + '_' + lower_joint + '_FK_JNT_01'

	fkIkSwitchName = name + '_' + side + '_' + limb + '_settings_cc_01.FK_IK'

	ikControlName = name + '_' + side + '_IK_' + limb + '_cc_01'
	ikPoleVectorName = name + '_' + side + '_' + limb + '_pole_vector_cc_01'

	fkUpperJointControlName = name + '_' + side + '_FK_upper_' + limb + '_cc_01'
	fkMiddleJointControlName = name + '_' + side + '_FK_lower_' + limb + '_cc_01'
	fkLowerJointControlName = name + '_' + side + '_FK_' + lower_joint + '_cc_01'

	snapIkToFk(fkUpperJointName, fkMiddleJointName, fkLowerJointName, ikControlName, ikPoleVectorName, fkIkSwitchName=fkIkSwitchName, fkUpperJointControlName=fkUpperJointControlName, fkMiddleJointControlName=fkMiddleJointControlName, fkLowerJointControlName=fkLowerJointControlName)

def fk_to_ik_match(name, limb, side):

	if limb == 'arm':
		lower_joint = 'wrist'
	elif limb == 'leg':
		lower_joint = 'ankle'

	fkIkSwitchName = name + '_' + side + '_' + limb + '_settings_cc_01.FK_IK'

	ikControlName = name + '_' + side + '_IK_' + limb + '_cc_01'
	ikPoleVectorName = name + '_' + side + '_' + limb + '_pole_vector_cc_01'

	fkUpperJointControlName = name + '_' + side + '_FK_upper_' + limb + '_cc_01'
	fkMiddleJointControlName = name + '_' + side + '_FK_lower_' + limb + '_cc_01'
	fkLowerJointControlName = name + '_' + side + '_FK_' + lower_joint + '_cc_01'

	ikUpperJointName = name + '_' + side + '_upper_' + limb + '_IK_JNT_01'
	ikMiddleJointName = name + '_' + side + '_lower_' + limb + '_IK_JNT_01'
	ikLowerJointName = name + '_' + side + '_' + lower_joint + '_IK_JNT_01'

	upperLimbLenControlName = name + '_' + side + '_' + limb + '_settings_cc_01.Upper_' + limb + '_Length'
	lowerLimbLenControlName = name + '_' + side + '_' + limb + '_settings_cc_01.Lower_' + limb + '_Length'

	snapFkToIk(ikUpperJointName, ikMiddleJointName, ikLowerJointName, fkUpperJointControlName, fkMiddleJointControlName, upperLimbLenControlName, lowerLimbLenControlName, fkLowerJointControlName=fkLowerJointControlName, fkIkSwitchName=fkIkSwitchName, ikControlName=ikControlName, ikPoleVectorName=ikPoleVectorName)

#Change from FK to IK
def snapIkToFk(fkUpperJointName, fkMiddleJointName, fkLowerJointName, ikControlName, ikPoleVectorName, fkIkSwitchName=None, fkUpperJointControlName=None, fkMiddleJointControlName=None, fkLowerJointControlName=None):
	# get location of FK skeleton
	fkShoulPos = np.array(cmds.xform(fkUpperJointName, q=True, ws=True, t=1))
	fkElbowPos = np.array(cmds.xform(fkMiddleJointName, q=True, ws=True, t=1))
	fkWristPos = np.array(cmds.xform(fkLowerJointName, q=True, ws=True, t=1))
	fkWristRot = np.array(cmds.xform(fkLowerJointName, q=True, ws=True, rotation=True))

	if fkIkSwitchName is not None:
		# switch mode from IK to FK
		cmds.setAttr(fkIkSwitchName, 1)

	# Calculate location of pole vector
	ikPolePos = fkToIk(fkShoulPos, fkElbowPos, fkWristPos)['ikPole']

	# snap IK controls to FK location
	cmds.setAttr(ikPoleVectorName + ".Follow", 3)
	print "Change the follow"
	cmds.xform(ikControlName, rotation=[fkWristRot[0],fkWristRot[1],fkWristRot[2]], ws=True)
	cmds.xform(ikControlName, translation=[fkWristPos[0],fkWristPos[1],fkWristPos[2]], ws=True)
	cmds.setAttr(ikPoleVectorName + ".Follow", 0)
	cmds.xform(ikPoleVectorName, translation=[ikPolePos[0],ikPolePos[1],ikPolePos[2]], ws=True)
	print "change the follow back"

	name = 'Grendel'
	side = 'RGT'
	limb = 'arm'
	lower_joint = 'wrist'
	ikUpperJointName = name + '_' + side + '_upper_' + limb + '_IK_JNT_01'
	ikMiddleJointName = name + '_' + side + '_lower_' + limb + '_IK_JNT_01'
	ikLowerJointName = name + '_' + side + '_' + lower_joint + '_IK_JNT_01'

	fksRot = cmds.xform(fkUpperJointName, q=True, ws=True, rotation=1)
	fkeRot = cmds.xform(fkMiddleJointName, q=True, ws=True, rotation=1)
	fkwRot = cmds.xform(fkLowerJointName, q=True, ws=True, rotation=1)
	iksRot = cmds.xform(ikUpperJointName, q=True, ws=True, rotation=1)
	ikeRot = cmds.xform(ikMiddleJointName, q=True, ws=True, rotation=1)
	ikwRot = cmds.xform(ikLowerJointName, q=True, ws=True, rotation=1)

	print fksRot
	print iksRot
	print fkeRot
	print ikeRot
	print fkwRot
	print ikwRot

	if fkUpperJointControlName is not None and fkMiddleJointControlName is not None and fkLowerJointControlName is not None:
		# Deselect the FK controls
		cmds.select(fkUpperJointControlName, deselect=True)
		cmds.select(fkMiddleJointControlName, deselect=True)
		cmds.select(fkLowerJointControlName, deselect=True)

#Change from IK to FK
def snapFkToIk(ikUpperJointName, ikMiddleJointName, ikLowerJointName, fkUpperJointControlName, fkMiddleJointControlName, upperLimbLenControlName, lowerLimbLenControlName, fkLowerJointControlName=None, fkIkSwitchName=None, ikControlName=None, ikPoleVectorName=None):
	# get location of IK skeleton
	ikUpperJointRot = np.array(cmds.xform(ikUpperJointName, q=True, ws=True, rotation=True))
	ikMiddleJointRot = np.array(cmds.xform(ikMiddleJointName, q=True, ws=True, rotation=True))
	ikLowerJointRot = np.array(cmds.xform(ikLowerJointName, q=True, ws=True, rotation=True))\

	# Get position of joints to calculate lengths
	ikUpperJointPos = np.array(cmds.xform(ikUpperJointName, q=True, ws=True, rp=True))
	ikMiddleJointPos = np.array(cmds.xform(ikMiddleJointName, q=True, ws=True, rp=True))
	ikLowerJointPos = np.array(cmds.xform(ikLowerJointName, q=True, ws=True, rp=True))

	# Calculate Lengths of upper and lower limbs
	upperLimbLen = np.linalg.norm(ikUpperJointPos - ikMiddleJointPos)
	lowerLimbLen = np.linalg.norm(ikMiddleJointPos - ikLowerJointPos)

	if fkIkSwitchName is not None:
		# switch mode from FK to IK
		cmds.setAttr(fkIkSwitchName, 0)

	# snap FK controls to IK location
	cmds.xform(fkUpperJointControlName, rotation=[ikUpperJointRot[0],ikUpperJointRot[1],ikUpperJointRot[2]], ws=True)
	cmds.xform(fkMiddleJointControlName, rotation=[ikMiddleJointRot[0],ikMiddleJointRot[1],ikMiddleJointRot[2]], ws=True)
	cmds.xform(fkLowerJointControlName, rotation=[ikLowerJointRot[0],ikLowerJointRot[1],ikLowerJointRot[2]], ws=True)

	# apply Lengths to limbs
	if False:
		# TODO: I need to do some more work on this before it will work. The problem is that the hights here are given as scalars and we can only figure out what the current length is. If we were able to get the original length then we could work with that. But I can't figure out how to get that yet.
		cmds.setAttr(upperLimbLenControlName, upperLimbLen)
		cmds.setAttr(lowerLimbLenControlName, lowerLimbLen)

	fksRot = cmds.xform(fkUpperJointName, q=True, ws=True, rotation=1)
	fkeRot = cmds.xform(fkMiddleJointName, q=True, ws=True, rotation=1)
	fkwRot = cmds.xform(fkLowerJointName, q=True, ws=True, rotation=1)
	iksRot = cmds.xform(ikUpperJointName, q=True, ws=True, rotation=1)
	ikeRot = cmds.xform(ikMiddleJointName, q=True, ws=True, rotation=1)
	ikwRot = cmds.xform(ikLowerJointName, q=True, ws=True, rotation=1)

	print fksRot
	print iksRot
	print fkeRot
	print ikeRot
	print fkwRot
	print ikwRot

	if ikControlName is not None and ikPoleVectorName is not None:
		# Deselect the IK controls
		cmds.select(ikControlName, deselect=True)
		cmds.select(ikPoleVectorName, deselect=True)

def fkToIk(fkShoulderPos, fkElbowPos, fkWristPos):
	'''
	parameters should be numpy arrays
	'''
	# Get pole vector
	# 1) Get point on plane
	midPoint = (fkWristPos + fkShoulderPos) / 2

	# 2) Get vector from point to middle joint (elbow or knee)
	halfPole = fkElbowPos - midPoint
	# 3) Extend vector to be in a good position for the pole vector
	pole = midPoint + (halfPole * 4)
	# ik lower joint (wrist or ankle) goes to same pos as fk lower joint
	return {'ikWristControl': fkWristPos, 'ikPole': pole}

from PySide2 import QtWidgets
from PySide2.QtWidgets import *

WINDOW_WIDTH = 250
WINDOW_HEIGHT = 100

def maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

class FKIKSnappingWindow(QDialog):
	def __init__(self, parent=maya_main_window()):
		QDialog.__init__(self, parent)
		self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
		self.create_layout()

	def create_layout(self):
		self.characterMenu = QtWidgets.QComboBox()
		self.characterMenu.addItem("grendel_rig_main_Grendel")
		self.characterMenu.addItem("beowulf_rig_main_Beowulf")
		self.characterMenu.addItem("viking_rig_main_Viking")
		self.characterMenu.addItem("viking_with_facial_rig_main_Viking")
		self.characterMenu.addItem("dragon_rig_main_Dragon")

		self.limbMenu = QtWidgets.QComboBox()
		self.limbMenu.addItem("arm")
		self.limbMenu.addItem("leg")

		self.sideMenu = QtWidgets.QComboBox()
		self.sideMenu.addItem("RGT")
		self.sideMenu.addItem("LFT")

		self.switchLabel = QLabel('Switch to: ')
		self.matchIkToFk = QPushButton('IK')
		self.matchIkToFk.clicked.connect(self.fillMatchIKToFK)
		self.matchFkToIk = QPushButton('FK')
		self.matchFkToIk.clicked.connect(self.fillMatchFKToIK)
		self.closeButton = QPushButton('Close')
		self.closeButton.clicked.connect(self.close_dialog)

		#Create button layout
		button_layout = QHBoxLayout()
		button_layout.setSpacing(2)
		button_layout.addStretch()

		button_layout.addWidget(self.switchLabel)
		button_layout.addWidget(self.matchIkToFk)
		button_layout.addWidget(self.matchFkToIk)
		button_layout.addWidget(self.closeButton)

		#Create main layout
		main_layout = QVBoxLayout()
		main_layout.setSpacing(2)
		main_layout.setMargin(2)
		main_layout.addWidget(self.characterMenu)
		main_layout.addWidget(self.limbMenu)
		main_layout.addWidget(self.sideMenu)
		main_layout.addLayout(button_layout)

		self.setLayout(main_layout)

	def fillMatchIKToFK(self):
		character = str(self.characterMenu.currentText())
		limb = str(self.limbMenu.currentText())
		side = str(self.sideMenu.currentText())
		ik_to_fk_match(character, limb, side)

	def fillMatchFKToIK(self):
		character = str(self.characterMenu.currentText())
		limb = str(self.limbMenu.currentText())
		side = str(self.sideMenu.currentText())
		fk_to_ik_match(character, limb, side)

	def close_dialog(self):
		self.close()

def go():
	dialog = FKIKSnappingWindow()
	dialog.show()

if __name__ == '__main__':
	go()
