from pymel.core import *

def tagGeo():
	selected_groups = ls(sl=True, tr=True)
	print selected_groups
	response = showConfirmationPopup(selected_groups)
	if response == "Yes":
		for obj in selected_groups:
			if not obj.hasAttr("BYU_Alembic_Export_Flag"):
				cmds.lockNode(str(obj), l=False) # node must be unlocked to add an attribute
				obj.addAttr("BYU_Alembic_Export_Flag", dv=True, at=bool, h=False, k=True)
		showSuccessPopup()

def showConfirmationPopup(selected_groups):
	return cmds.confirmDialog( title         = 'Add Alembic Tag'
		                         , message       = 'Add Alembic Tag to:\n' + str(selected_groups)
		                         , button        = ['Yes', 'No']
		                         , defaultButton = 'Yes'
		                         , cancelButton  = 'No'
		                         , dismissString = 'No')

def showSuccessPopup():
	return cmds.confirmDialog( title         = 'Success'
		                         , message       = 'Alembic Tags were successfully added.'
		                         , button        = ['OK']
		                         , defaultButton = 'OK'
		                         , cancelButton  = 'OK'
		                         , dismissString = 'OK')

def go():
	tagGeo()
	
