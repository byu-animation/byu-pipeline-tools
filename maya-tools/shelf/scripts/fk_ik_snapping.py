'''
Things of interest:
	Grendel_LFT_arm_pole_vector_cc_01
	Grendel_LFT_IK_arm_cc_01

	Grendel_LFT_FK_upper_arm_cc_01
	Grendel_LFT_FK_lower_arm_cc_01
	Grendel_LFT_FK_wrist_cc_01
'''
import numpy as np

#Change from FK to IK
def snapIkToFk():
	fkShoulPos = np.array(cmds.xform("Grendel_LFT_upper_arm_FK_JNT_01", q=True, ws=True, rp=1))
	fkElbowPos = np.array(cmds.xform("Grendel_LFT_lower_arm_FK_JNT_01", q=True, ws=True, rp=1))
	fkWristPos = np.array(cmds.xform("Grendel_LFT_wrist_FK_JNT_01", q=True, ws=True, rp=1))
	fkWristRot = np.array(cmds.xform('Grendel_LFT_wrist_FK_JNT_01', q=True, ws=True, rotation=True))

	print fkShoulPos
	print fkElbowPos
	print fkWristPos

	cmds.setAttr("Grendel_LFT_arm_settings_cc_01.FK_IK", 1)
	ikPolePos = fkToIk(fkShoulPos, fkElbowPos, fkWristPos)['ikPole']
	print ikPolePos

	cmds.xform("Grendel_LFT_IK_arm_cc_01", translation=[fkWristPos[0],fkWristPos[1],fkWristPos[2]], ws=1)
	cmds.xform('Grendel_LFT_IK_arm_cc_01', rotation=[fkWristRot[0],fkWristRot[1],fkWristRot[2]], ws=1)
	cmds.xform("Grendel_LFT_arm_pole_vector_cc_01", translation=[ikPolePos[0],ikPolePos[1],ikPolePos[2]], ws=1)

#Change from IK to FK
def snapFkToIk():
	cmds.setAttr("Grendel_LFT_arm_settings_cc_01.FK_IK", 1)
	cmds.setAttr("Grendel_LFT_FK_upper_arm_cc_01.t",trans[0],trans[1],trans[2])
	cmds.setAttr("Grendel_LFT_FK_upper_arm_cc_01.r",rot[0],rot[1],rot[2])

	cmds.setAttr("Grendel_LFT_FK_lower_arm_cc_01.t",trans[0],trans[1],trans[2])
	cmds.setAttr("Grendel_LFT_FK_lower_arm_cc_01.r",rot[0],rot[1],rot[2])

	cmds.setAttr("Grendel_LFT_FK_wrist_cc_01.t",trans[0],trans[1],trans[2])
	cmds.setAttr("Grendel_LFT_FK_wrist_cc_01.r",rot[0],rot[1],rot[2])

def ikToFk(ikWrist, ikPole):
	return {'fkShoulder': fkShoulder, 'fkElbow': fkElbow, 'fkWrist': fkWrist}

def fkToIk(fkShoulderPos, fkElbowPos, fkWristPos):
	'''
	parameters should be numpy arrays
	'''
	# Get pole vector
	# 1) Get point on plane
	point_on_plane = fkWristPos + ((fkShoulderPos-fkWristPos)/2)
	print "point_on_plane: " + str(point_on_plane)
	# 2) Get vector from point to elbow
	halfPole = fkElbowPos - point_on_plane
	print "halfPole: " + str(halfPole)
	# 3) Extend vector to be in a good position for the pole vector
	pole = fkElbowPos + (halfPole * 2)
	# ik wrist goes to same pos as fk wrist
	return {'ikWristControl': fkWristPos, 'ikPole': pole}
