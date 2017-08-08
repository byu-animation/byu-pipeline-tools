import numpy as np

ik_to_fk_match('Grendel', 'arm', 'LFT')
ik_to_fk_match('Grendel', 'arm', 'RGT')

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

	ikShoulderName = name + '_' + side + '_upper_' + limb + '_IK_JNT_01'
	ikElbowName = name + '_' + side + '_lower_' + limb + '_IK_JNT_01'
	ikWristName = name + '_' + side + '_' + lower_joint + '_IK_JNT_01'

	snapFkToIk(ikShoulderName, ikElbowName, ikWristName, fkUpperJointControlName, fkMiddleJointControlName, fkLowerJointControlName=fkLowerJointControlName, fkIkSwitchName=fkIkSwitchName, ikControlName=ikControlName, ikPoleVectorName=ikPoleVectorName)

#Change from FK to IK
def snapIkToFk(fkUpperJointName, fkMiddleJointName, fkLowerJointName, ikControlName, ikPoleVectorName, fkIkSwitchName=None, fkUpperJointControlName=None, fkMiddleJointControlName=None, fkLowerJointControlName=None):
	# get location of FK skeleton
	fkShoulPos = np.array(cmds.xform(fkUpperJointName, q=True, ws=True, rp=1))
	fkElbowPos = np.array(cmds.xform(fkMiddleJointName, q=True, ws=True, rp=1))
	fkWristPos = np.array(cmds.xform(fkLowerJointName, q=True, ws=True, rp=1))
	fkWristRot = np.array(cmds.xform(fkLowerJointName, q=True, ws=True, rotation=True))

	if fkIkSwitchName is not None:
		# switch mode from IK to FK
		cmds.setAttr(fkIkSwitchName, 1)

	# Calculate location of pole vector
	ikPolePos = fkToIk(fkShoulPos, fkElbowPos, fkWristPos)['ikPole']

	# snap IK controls to FK location
	cmds.xform(ikControlName, translation=[fkWristPos[0],fkWristPos[1],fkWristPos[2]], ws=True)
	cmds.xform(ikControlName, rotation=[fkWristRot[0],fkWristRot[1],fkWristRot[2]], ws=True)
	cmds.xform(ikPoleVectorName, translation=[ikPolePos[0],ikPolePos[1],ikPolePos[2]], ws=True)

	if fkUpperJointControlName is not None and fkMiddleJointControlName is not None and fkLowerJointControlName is not None:
		# Deselect the FK controls
		cmds.select(fkUpperJointControlName, deselect=True)
		cmds.select(fkMiddleJointControlName, deselect=True)
		cmds.select(fkLowerJointControlName, deselect=True)

#Change from IK to FK
def snapFkToIk(ikShoulderName, ikElbowName, ikWristName, fkUpperJointControlName, fkMiddleJointControlName, fkLowerJointControlName=None, fkIkSwitchName=None, ikControlName=None, ikPoleVectorName=None):
	# get location of IK skeleton
	ikShoulPos = np.array(cmds.xform(ikShoulderName, q=True, ws=True, rotation=True))
	ikElbowPos = np.array(cmds.xform(ikElbowName, q=True, ws=True, rotation=True))
	ikWristPos = np.array(cmds.xform(ikWristName, q=True, ws=True, rotation=True))

	if fkIkSwitchName is not None:
		# switch mode from FK to IK
		cmds.setAttr(fkIkSwitchName, 0)

	# snap FK controls to IK location
	cmds.xform(fkUpperJointControlName, rotation=[ikShoulPos[0],ikShoulPos[1],ikShoulPos[2]], ws=True)
	cmds.xform(fkMiddleJointControlName, rotation=[ikElbowPos[0],ikElbowPos[1],ikElbowPos[2]], ws=True)
	cmds.xform(fkLowerJointControlName, rotation=[ikWristPos[0],ikWristPos[1],ikWristPos[2]], ws=True)

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
	point_on_plane = fkWristPos + ((fkShoulderPos-fkWristPos)/2)
	# 2) Get vector from point to elbow
	halfPole = fkElbowPos - point_on_plane
	# 3) Extend vector to be in a good position for the pole vector
	pole = fkElbowPos + (halfPole * 2)
	# ik wrist goes to same pos as fk wrist
	return {'ikWristControl': fkWristPos, 'ikPole': pole}
