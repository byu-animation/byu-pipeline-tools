import pymel.core as pm
import reference
import attach_beard
import alembic_exporter
from byuam import Project
import os
import re

beards = ["3","5","6","7","8",]

beardRoot = "viking_beard_1_rig_main_"
beardSufix = ["Beard3", "BEARD_5", "BEARD_RIG","BEARD_RIG","BEARD8"]
beardGeoSufix = ["Geo", "GEO", "GEO","GEO","GEO"]

def go():
	project = Project()
	checkout_element = project.get_checkout_element(os.path.dirname(pm.sceneName()))
	beardDir = os.path.join(checkout_element.get_dir(), "beards")
	if not os.path.exists(beardDir):
		os.makedirs(beardDir)

	# Select viking components
	viking = pm.ls(selection=True)[0]
	vikingName = viking.name()
	vikingPrefix = re.search( r'\w*:?\w*Viking', vikingName, re.I).group()
	vikingHead = vikingPrefix + '_head_cc_01'
	vikingJaw = vikingPrefix + '_jaw_cc_01'
	vikingCog = vikingPrefix + '_COG_cc_01'
	vikingChest = vikingPrefix + '_chest_cc_01'
	vikingUpBelly = vikingPrefix + '_UPP_belly_cc_01'
	vikingMidBelly = vikingPrefix + '_MID_belly_cc_01'
	vikingLoBelly = vikingPrefix + '_LOW_belly_cc_01'
	vikingPrimary = vikingPrefix + '_primary_global_cc_01'

	# Set keyframes
	pm.currentTime( 0, edit=True )
	pm.setKeyframe(vikingHead, vikingJaw, vikingCog, vikingChest, vikingUpBelly, vikingMidBelly, vikingLoBelly, vikingPrimary, i=True)
	pm.currentTime( -10, edit=True )
	pm.setKeyframe(vikingHead, vikingJaw, vikingCog, vikingChest, vikingUpBelly, vikingMidBelly, vikingLoBelly, vikingPrimary, v=0, at=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ'])

	pm.currentTime(0, edit=True)

	for i, beard in enumerate(beards):
		print "Starting beard " + beard
		paths = {"/groups/grendel/production/assets/viking_beard_" + beard + "/rig/main/viking_beard_" + beard + "_rig_main.mb"}

		#Reference the beards
		reference.reference(paths)

		#Attach the beards
		beardName = beardRoot.replace("1", beard) + beardSufix[i]
		pm.select(beardName)
		pm.select(viking, add=True)
		selection = pm.ls(selection=True)
		#Move to where the viking is in A-Pose
		pm.currentTime(-10, edit=True)
		if len(selection) == 2:
			pm.Mel.eval(attach_beard.attachBeard())
		else:
			print "There was an error with the selection"

		#Export the beards
		abcFile = os.path.join(beardDir, "BEARD" + beard + "_base.abc")
		endFrame = pm.playbackOptions(q=True, maxTime=True)
		beardGeo = beardRoot.replace("1", beard) + beardGeoSufix[i]
		pm.select(beardGeo)
		exportSelection = pm.ls(selection=True)
		pm.Mel.eval(alembic_exporter.buildAlembicCommand(abcFile, 1, endFrame, geoList=exportSelection))

		print "Ending beard " + beard
