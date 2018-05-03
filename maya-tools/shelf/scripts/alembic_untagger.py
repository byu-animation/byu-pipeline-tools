from pymel.core import *

def untagGeo():
	selected_groups = ls(sl=True, tr=True)
	print selected_groups
	response = showConfirmationPopup(selected_groups)
	if response == "Yes":
		for obj in selected_groups:
			if obj.hasAttr("BYU_Alembic_Export_Flag"):
				obj.deleteAttr("BYU_Alembic_Export_Flag")
		showSuccessPopup()

def showConfirmationPopup(selected_groups):
	return cmds.confirmDialog( title         = 'Remove Alembic Tag'
		                         , message       = 'Remove Alembic Tag from:\n' + str(selected_groups)
		                         , button        = ['Yes', 'No']
		                         , defaultButton = 'Yes'
		                         , cancelButton  = 'No'
		                         , dismissString = 'No')

def showSuccessPopup():
	return cmds.confirmDialog( title         = 'Success'
		                         , message       = 'Alembic Tags were successfully removed.'
		                         , button        = ['OK']
		                         , defaultButton = 'OK'
		                         , cancelButton  = 'OK'
		                         , dismissString = 'OK')

def go():
	untagGeo()
