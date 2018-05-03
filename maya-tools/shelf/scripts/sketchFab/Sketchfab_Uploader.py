import re, subprocess, os, shutil
from maya import OpenMayaUI as omui
from maya import OpenMaya as om
import maya.cmds as cmds
if int(cmds.about(version=True)[0:4]) < 2017:
	from PySide.QtCore import *
	from PySide.QtGui import *
	from PySide.QtUiTools import *
	from shiboken import wrapInstance
else:
	from PySide2.QtCore import *
	from PySide2.QtGui import *
	from PySide2.QtUiTools import *
	from PySide2.QtWidgets import *
	from shiboken2 import wrapInstance
from functools import partial
import tempfile, os, json, base64
from time import sleep
import requests

class Sketchfab_Uploader:

	# environment settings
	maya_install_folder = os.getenv("MAYA_LOCATION")
	script_folder = os.path.dirname(os.path.realpath(__file__))
	uif_main = script_folder+"/Sketchfab_Uploader.ui"
	uif_settings = script_folder+"/Sketchfab_Settings.ui"
	SKETCHFAB_DOMAIN = 'sketchfab.com'
	SKETCHFAB_API_URL = 'https://api.{}/v2/models'.format(SKETCHFAB_DOMAIN)
	SKETCHFAB_MODEL_URL = 'https://{}/models/'.format(SKETCHFAB_DOMAIN)
	about_sf_uploader = "Sketchfab Uploader by www.ticket01.com (build 141128)"

	def __init__(self):
		# get parent pointer
		mayaMainWindowPtr = omui.MQtUtil.mainWindow()
		if mayaMainWindowPtr is not None:
			self.mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QMainWindow)
		else:
			print("Maya main window could not be found. Bailing out.")
			return
		# load main window
		self.createUI(self.mayaMainWindow)
		if not cmds.optionVar(exists="sfApiToken"):
			cmds.optionVar(sv=("sfApiToken", ""))
		if not cmds.optionVar(exists="sfDefaultTags"):
			cmds.optionVar(sv=("sfDefaultTags", ""))

	def createUI(self, parent):
		# main window
		loader = QUiLoader()
		file = QFile(self.uif_main)
		file.open(QFile.ReadOnly)
		self.ui_main = loader.load(file, parent)
		file.close()
		self.ui_main.setWindowFlags(Qt.Window)
		self.ui_main.show()
		# settings menu
		file = QFile(self.uif_settings)
		file.open(QFile.ReadOnly)
		self.ui_settings = loader.load(file, self.ui_main)
		file.close()
		self.ui_settings.setWindowFlags(Qt.Window)
		#
		self.ui_main.actionSketchfab_settings.triggered.connect(self.showSettingsDialog)
		self.ui_settings.accepted.connect(self.saveSettings)
		self.ui_main.bUploadToSketchfab.clicked.connect(self.prepareAndUpload)

		self.ui_main.cbPrivate.toggled.connect(self.togglePasswordField)

		self.ui_main.statusbar.showMessage(self.about_sf_uploader)

		self.ui_main.lModelURL.setStyleSheet("background-color: #777;color:grey;padding:2px;border-radius:2px;");

	def togglePasswordField(self, checked):
		self.ui_main.lPassword.setEnabled(checked)
		self.ui_main.lePassword.setEnabled(checked)

	def saveSettings(self):
		cmds.optionVar(sv=("sfApiToken", self.ui_settings.leApiToken.text()))
		cmds.optionVar(sv=("sfDefaultTags", self.ui_settings.leDefaultTags.text()))

	def showSettingsDialog(self):
		self.ui_settings.leApiToken.setText(cmds.optionVar(query="sfApiToken"))
		self.ui_settings.leDefaultTags.setText(cmds.optionVar(query="sfDefaultTags"))
		self.ui_settings.show()

	def prepareAndUpload(self):
		self.ui_main.statusbar.showMessage("Exporting model to FBX format")
		# create a temporary directory
		tmp_dir = tempfile.mkdtemp()
		base_name = '%s/maya2sketchfab' % tmp_dir
		model_file = '%s.fbx' % base_name

		# Set options
		import maya.mel as Mm
		# Force textures embedding
		Mm.eval('FBXExportEmbeddedTextures -v true')
		# Force binary fbx export (smaller size)
		Mm.eval('FBXExportInAscii  -v false')

		# for some reason Maya fails to export to this location when the file does not yet exist
		# create a dummy file with zero length that has the same name
		open(model_file, 'w').close()
		# export Maya scene as FBX
		cmds.file(model_file, force=True, exportAll=True, preserveReferences=True, type="FBX export")
		# create a screen shot and save as .png
		thumb_file_name = '%s.png' % base_name
		buffer = om.MImage()
		omui.M3dView.active3dView().readColorBuffer(buffer, True)
		buffer.resize(448, 280, True)
		buffer.writeToFile(thumb_file_name, 'png')

		# parameters
		private = 1 if self.ui_main.cbPrivate.isChecked() else 0
		autopublish = 1 if self.ui_main.cbAutopublish.isChecked() else 0
		password = self.ui_main.lePassword.text() if private else ""
		tags = cmds.optionVar(query="sfDefaultTags")+" "+self.ui_main.leTags.text()
		maya_version = cmds.about(version=True).replace(" ", "_")

		data = {
			'token': cmds.optionVar(query="sfApiToken"),
			'name': self.ui_main.leModelName.text(),
			'description': self.ui_main.pteDescription.toPlainText(),
			'tags': tags + ' maya',
			'private': private,
			'isPublished': autopublish,
			'password': password,
			'source': 'maya-' + maya_version
		}

		f = open(model_file, 'rb')

		files = {
			'modelFile': f
		}

		try:
			model_uid = self.uploadToSketchfab(data, files)
			self.poll_processing_status(model_uid)
		finally:
			f.close()

	def uploadToSketchfab(self, data, files):

		try:
			r = requests.post(self.SKETCHFAB_API_URL, data=data, files=files, verify=False)
		except requests.exceptions.RequestException as e:
			self.ui_main.statusbar.showMessage("An error occured: {}".format(e))
			return

		result = r.json()

		if r.status_code != requests.codes.created:
			self.ui_main.statusbar.showMessage("Upload failed with error: {}".format(result))
			return

		model_uid = result['uid']
		model_url = self.SKETCHFAB_MODEL_URL + model_uid
		self.ui_main.statusbar.showMessage("Upload successful. Your model is being processed.")
		self.ui_main.statusbar.showMessage("Once the processing is done, the model will be available at: {}".format(model_url))

		return model_uid

	def poll_processing_status(self, model_uid):
		polling_url = "{}/{}/status?token={}".format(self.SKETCHFAB_API_URL, model_uid, cmds.optionVar(query="sfApiToken"))
		max_errors = 10
		errors = 0
		retry = 0
		max_retries = 50
		retry_timeout = 5 # seconds

		while (retry < max_retries) and (errors < max_errors):
			self.ui_main.statusbar.showMessage("Try polling processing status (attempt #{}) ...".format(retry))

			try:
				r = requests.get(polling_url)
			except requests.exceptions.RequestException as e:
				self.ui_main.statusbar.showMessage("Try failed with error {}".format(e))
				errors += 1
				retry += 1
				continue

			result = r.json()

			if r.status_code != requests.codes.ok:
				self.ui_main.statusbar.showMessage("Upload failed with error: {}".format(result['error']))
				errors += 1
				retry += 1
				continue

			processing_status = result['processing']
			if processing_status == 'PENDING':
				self.ui_main.statusbar.showMessage("Your model is in the processing queue. Will retry in {} seconds".format(retry_timeout))
				#print "Want to skip the line? Get a pro account! https://sketchfab.com/plans"
				retry += 1
				sleep(retry_timeout)
				continue
			elif processing_status == 'PROCESSING':
				self.ui_main.statusbar.showMessage("Your model is still being processed. Will retry in {} seconds".format(retry_timeout))
				retry += 1
				sleep(retry_timeout)
				continue
			elif processing_status == 'FAILED':
				self.ui_main.statusbar.showMessage("Processing failed: {}".format(result['error']))
				return
			elif processing_status == 'SUCCEEDED':
				model_url = self.SKETCHFAB_MODEL_URL + model_uid
				self.ui_main.statusbar.showMessage("Model uploaded.")
				self.ui_main.lModelURL.setText('<a href="'+model_url+'">'+model_url+'</a>')
				return

			retry += 1

		self.ui_main.statusbar.showMessage("Stopped polling after too many retries or too many errors")
