from PySide2 import QtWidgets
from PySide2.QtWidgets import *

import maya.cmds as cmds
import maya.OpenMayaUI as omu
from pymel.core import *
# import utilities as amu #asset manager utilities
import os
import byuam
from byuam.environment import Environment, Department
from byuam.project import Project
from byugui import message_gui
import alembic_export_common as abcCom

WINDOW_WIDTH = 330
WINDOW_HEIGHT = 300

def maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.qApp.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

class AlembicExportDialog(QDialog):
	def __init__(self, parent=maya_main_window(), cfx=False):
	#def setup(self, parent):
		QDialog.__init__(self, parent)
		self.saveFile()
		self.setWindowTitle('Select Objects for Export')
		self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
		self.create_layout()
		self.create_connections(cfx=cfx)
		self.create_export_list()

	def create_layout(self):
		#Create the selected item list
		self.selection_list = QListWidget()
		self.selection_list.setSelectionMode(QAbstractItemView.ExtendedSelection);
		self.selection_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

		#Create Export Alembic and Cancel buttons
		self.export_button = QPushButton('Export Alembic')
		self.cancel_button = QPushButton('Cancel')

		#Create button layout
		button_layout = QHBoxLayout()
		button_layout.setSpacing(2)
		button_layout.addStretch()

		button_layout.addWidget(self.export_button)
		button_layout.addWidget(self.cancel_button)

		#Create main layout
		main_layout = QVBoxLayout()
		main_layout.setSpacing(2)
		main_layout.setMargin(2)
		main_layout.addWidget(self.selection_list)
		main_layout.addLayout(button_layout)

		self.setLayout(main_layout)

	def create_connections(self, cfx=False):
		#Connect the buttons
		#self.connect(self.export_button, SIGNAL('clicked()'), self.export_alembic)
		#self.connect(self.cancel_button, SIGNAL('clicked()'), self.close_dialog)
		self.export_button.clicked.connect(lambda: self.export_alembic(cfx=cfx))
		self.cancel_button.clicked.connect(self.close_dialog)

	def create_export_list(self):
		#Remove all items from the list before repopulating
		self.selection_list.clear()

		#Add the list to select from
		loadedRef = self.getLoadedReferences()

		for ref in loadedRef:
			item = QListWidgetItem(ref)
			item.setText(ref)
			self.selection_list.addItem(item)

		self.selection_list.sortItems()

	def getLoadedReferences(self):
		references = cmds.ls(references=True)
		loaded=[]
		print "Loaded References: "
		for ref in references:
			print "Checking status of " + ref
			try:
				if cmds.referenceQuery(ref, isLoaded=True):
					loaded.append(ref)
			except:
				print "Warning: " + ref + " was not associated with a reference file"
		return loaded


	########################################################################
	# SLOTS
	########################################################################

	def get_filename_for_reference(self, ref):
		refPath = cmds.referenceQuery(unicode(ref), filename=True)
		start = refPath.find("{")
		end = refPath.find("}")
		if start == -1 or end == -1:
			copyNum = ""
		else:
			copyNum = refPath[start+1:end]
		return os.path.basename(refPath).split('.')[0] + str(copyNum) + '.abc'

	def export_alembic(self, cfx=False):
		self.saveFile()

		# Start the export 5 frames before the beginning and end it 5 frames after the end for reason? I don't know I didn't write it. But I'm sure it's important.
		start_frame = cmds.playbackOptions(q=1, animationStartTime=True) - 5
		end_frame = cmds.playbackOptions(q=1, animationEndTime=True) + 5

		selectedReferences = []
		selectedItems = self.selection_list.selectedItems()
		print "HERE IS WHERE WE HAVE THE LIST OF SELECTED ITEMS: " + str(selectedItems)
		for item in selectedItems:
			print item.text()
			selectedReferences.append(item.text())
		print "Here are the references: ", selectedReferences

		if self.showConfirmAlembicDialog(selectedReferences) == 'Yes':
			loadPlugin("AbcExport")
			filePath = cmds.file(q=True, sceneName=True)
			fileDir = os.path.dirname(filePath)

			proj = Project()
			checkout = proj.get_checkout(fileDir)
			body = proj.get_body(checkout.get_body_name())
			dept = checkout.get_department_name()
			elem = body.get_element(dept, checkout.get_element_name())
			cfxElem = body.get_element(Department.CFX, checkout.get_element_name())
			print "We are looking at the cfx stuff right now"
			if cfx:
				abcFilePath = cfxElem.get_cache_dir()
			else:
				abcFilePath = elem.get_cache_dir()

			for ref in selectedReferences:
				print "Preparing", ref, "for export."
				refAbcFilePath = os.path.join(abcFilePath, self.get_filename_for_reference(ref))
				print "fileName for reference", self.get_filename_for_reference(ref)
				print "just before going in abcFilePath", refAbcFilePath
				try:
					command = abcCom.build_tagged_alembic_command(ref, refAbcFilePath, start_frame, end_frame)
					print "Command:", command
				except Exception:
					self.showNoTagFoundDialog(unicode(ref))
					print "We are in this exception"
					self.close_dialog()
					return
				print "Export Alembic command: ", command
				Mel.eval(command)
				os.system('chmod 774 ' + refAbcFilePath)

		self.close_dialog()

	def saveFile(self):
		if not cmds.file(q=True, sceneName=True) == '':
			cmds.file(save=True, force=True) #save file

	def showConfirmAlembicDialog(self, references):
		return cmds.confirmDialog( title		 = 'Export Alembic'
								 , message	   = 'Export Alembic for:\n' + str(references)
								 , button		= ['Yes', 'No']
								 , defaultButton = 'Yes'
								 , cancelButton  = 'No'
								 , dismissString = 'No')

	def showNoTagFoundDialog(self, ref):
		return cmds.confirmDialog( title		 = 'No Alembic Tag Found'
								 , message	   = 'Unable to locate Alembic Export tag for ' + ref + '.'
								 , button		= ['OK']
								 , defaultButton = 'OK'
								 , cancelButton  = 'OK'
								 , dismissString = 'OK')

	def close_dialog(self):
		self.close()

def go(cfx=False):
	dialog = AlembicExportDialog(cfx=cfx)
	dialog.show()

if __name__ == '__main__':
	go()
