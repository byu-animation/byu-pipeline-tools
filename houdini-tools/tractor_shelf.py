from PySide2 import QtGui, QtWidgets, QtCore
import pyqt_houdini
from TrHttpRPC import TrHttpRPC
import getpass
import urllib
import datetime
import os
import re
import shutil
import hou
from byugui import message_gui

# Project name (e.g. owned, ramshorn)
project_name = "dusk"
# Nodes to export
mantra_nodes = []

# Creates the dialog box
class ExportDialog(QDialog):
	empty_text = "delete me"
	def __init__(self, parent=None):
		QDialog.__init__(self, parent)
		vbox = QVBoxLayout()
		# Job name
		self.job_name = QLineEdit(self.empty_text)
		self.job_name.selectAll()
		name_layout = QHBoxLayout()
		name_layout.addWidget(QLabel("Job Name:"))
		name_layout.addWidget(self.job_name)
		vbox.addLayout(name_layout)
		# Priority
		self.priority = QComboBox()
		priority_opt = ["Very Low", "Low", "Medium", "High", "Very High"]
		for opt in priority_opt:
			self.priority.addItem(opt)
		self.priority.setCurrentIndex(2)
		# Begin time
		self.delay = QComboBox()
		delay_opts = ["Immediate", "Manual", "Delayed"]
		for opt in delay_opts:
			self.delay.addItem(opt)
		self.delay.currentIndexChanged.connect(self.delaytime)
		# Combo box options layout
		opts_layout = QHBoxLayout()
		opts_layout.addWidget(QLabel("Priority:"))
		opts_layout.addWidget(self.priority)
		opts_layout.addWidget(QLabel("Begin:"))
		opts_layout.addWidget(self.delay)
		opts_layout.addStretch()
		vbox.addLayout(opts_layout)
		# Time-frame selection for delayed jobs
		self.delay_time = QLineEdit("5")
		self.delay_unit = QComboBox()
		delay_unit_opts = ["mins","hours","days"]
		for opt in delay_unit_opts:
			self.delay_unit.addItem(opt)
		self.delay_unit.setCurrentIndex(0)
		# Delay time layout
		self.delay_layout = QHBoxLayout()
		self.delay_layout.addWidget(QLabel("Delay time:"))
		self.delay_layout.addWidget(self.delay_time)
		self.delay_layout.addWidget(self.delay_unit)
		self.delay_layout.addStretch()
		self.delaytime(0)
		vbox.addLayout(self.delay_layout)
		# Mantra node selection list
		self.select = QListWidget()
		self.select.setSelectionMode(QAbstractItemView.ExtendedSelection)
		for node in mantra_nodes:
			item = QListWidgetItem(node.name())
			self.select.addItem(item)
			# must come after adding to widget
			item.setSelected(True)
		vbox.addWidget(self.select)
		# Buttons
		self.export_btn = QPushButton('Export')
		self.export_btn.clicked.connect(self.export)
		self.cancel_btn = QPushButton('Cancel')
		self.cancel_btn.clicked.connect(self.close)
		btn_layout = QHBoxLayout()
		btn_layout.addWidget(self.cancel_btn)
		btn_layout.addWidget(self.export_btn)
		vbox.addLayout(btn_layout)
		# Window layout
		self.setFixedSize(360, 420)
		self.setWindowTitle("Confirm Export")
		self.setLayout(vbox)

	# Show/Hide the delay-time options
	def delaytime(self, index):
		i = 0
		items = self.delay_layout.count()
		while i<items:
			 item = self.delay_layout.itemAt(i).widget()
			 if item:
				 item.setVisible(index == 2)
			 i = i+1

	# Export selected mantra nodes for rendering
	def export(self):
		self.close()
		# Create a folder specifically for this job
		user = getpass.getuser()
		time_now = datetime.datetime.now()
	#Changed the ifd_dir to match Taijitu filepaths - Nick Evans 10/12/2016
		ifd_dir = "/groups/"+project_name+"/ifds/"+user+"_"+time_now.strftime("%m%d%y_%H%M%S")
	print "ifd_dir", ifd_dir, " mantra_nodes size: ", len(mantra_nodes)
		os.makedirs(ifd_dir)
		# Sanitize job title
		title = re.sub(r'[{}"\']', "", str(self.job_name.text())).strip(' \t\n\r')
		if len(title) == 0:
			title = self.empty_text
		# This is the alfred/tractor script we send to engine
		job_script = "Job -title {"+title+"} -metadata {Spooled by "+user+"} -init {\n\tAssign ifddir {"+ifd_dir+"}\n} -service {PixarRender} -subtasks {"
		# Loop through each frame of our nodes and create frame tasks
		index = -1
		for node in mantra_nodes:
			# Make sure this node was selected for export
			index = index+1
			print node.name();
			if self.select.item(index).isSelected():
				name = node.name()
				start = int(node.parm('f1').eval())
				end = int(node.parm('f2').eval())
				step = int(node.parm('f3').eval())
				job_script += "\n\tTask {"+("%s [%d-%d]" % (name, start, end))+"} -subtasks {"
				# Activate ifd output
				node.parm('soho_outputmode').set(True)
				node.parm('soho_diskfile').set(ifd_dir+('/%s_$F04.ifd' % name))
				# Loop through every frame in framerange
				for frame in range(start, end+1, step):
					job_script += "\n\t\tTask {Frame %04d} -cmds { RemoteCmd {./mantra -V a4 -f $ifddir/%s_%04d.ifd} }" % (frame, name, frame)
					# Render this frame to the ifd file
					node.render([frame, frame])
				job_script += "\n\t}"
				# Deactivate ifd output
				node.parm('soho_outputmode').set(False)
				node.parm('soho_diskfile').set("")
		job_script += "\n} -cleanup { RemoteCmd {rm -rf "+ifd_dir+"/} }"
		choice = True
		while choice:
			rc, msg = self.spool(job_script, time_now)
			# An error occurred
			if rc != 0:
				choice = hou.ui.displayMessage(
					"Failed to export to tractor!\nError Code #%d:\n%s\n\nDo you want to try again?" % (rc, msg),
					('Cancel', 'Retry'),
					hou.severityType.Warning
				)
			# Job succesfully spooled
			else:
				break
		#Cleanup ifd files, if they didn't want to retry
		if not choice:
			shutil.rmtree(ifd_dir)
	#After the export is done clear the mantra_nodes array - Ben DeMann 10/17/2016
	del mantra_nodes[:]
	print "Export Finished!"

	# Spool the generated script to the engine
	def spool(self, job_script, time_now):
		delay_type = self.delay.currentIndex()
		# Spool parameters
		spool_url = "spool?"
		# Current user will own this job
		spool_url += "jobOwner=" + urllib.quote("render") #getpass.getuser()
		# Location of mantra executable
		spool_url += "&cwd=" + urllib.quote("/opt/hfs.current/bin/")
		# Job priority (1=vlo, 2=lo, 3=med, 4=hi, 5=vhi)
		# Negating priority pauses the job on start
		priority = self.priority.currentIndex()+1
		if delay_type == 1:
			priority = -priority
		spool_url += "&priority=" + str(priority)
		# Wait until the specified time before starting (MM DD HH:MM)
		if delay_type == 2:
			sec = float(self.delay_time.text())
			unit = self.delay_unit.currentIndex()
			# 0=min, 1=hour, 2=day
			sec *= 60
			if unit > 0:
				sec *= 60
			if unit > 1:
				sec *= 24
			sec = int(sec)
			if sec > 0:
				time_delay = time_now + datetime.timedelta(0, sec)
				spool_url += "&aftertime=" + urllib.quote(time_delay.strftime("%m %d %H:%M"))
		# Tractor engine hostname
		rpc = TrHttpRPC("tractor-engine")
		# Send request to tractor engine
		return rpc.Transaction(
			spool_url, job_script,
			xheaders={"Content-Type": "application/tractor-spool"}
		)

def go():
	# Get all mantra nodes for export
	for node in hou.node("/out").children():
		# Make sure this is a mantra node, and not something else
		#if node.type().name() == "ifd":
		#EDIT FOR TAIJITU, remove generic mantra reference and add reference to cameras digital asset - Trevor Barrus 10/11/16
		if node.type().name() == "dusk_cameras":
			# Check each checkbox 1 for true (render) 0 for false (do not render) - Nick Evans 10/11/2016
			ten_checkbox = node.parm('tenCheck').evalAsInt()
			jampa_checkbox = node.parm('jampaCheck').evalAsInt()
			background_checkbox = node.parm('backgroundCheck').evalAsInt()
			foreground_checkbox = node.parm('foregroundCheck').evalAsInt()
			entrance_checkbox = node.parm('entranceCheck').evalAsInt()
			props_checkbox = node.parm('propsCheck').evalAsInt()
			effects_checkbox = node.parm('effectsCheck').evalAsInt()
			shadow_checkbox = node.parm('parm').evalAsInt()

			#Check the checkboxes, if checked for render add to mantra_nodes - Nick Evans 10/11/16
			if ten_checkbox > 0:
				mantra_nodes.append(node.node("dusk_ten"))
			if jampa_checkbox > 0:
				mantra_nodes.append(node.node("dusk_jampa"))
			if background_checkbox > 0:
				mantra_nodes.append(node.node("dusk_background"))
			if foreground_checkbox > 0:
				mantra_nodes.append(node.node("dusk_foreground"))
			if entrance_checkbox > 0:
				mantra_nodes.append(node.node("dusk_entrance"))
			if props_checkbox > 0:
				mantra_nodes.append(node.node("dusk_props"))
			if effects_checkbox > 0:
				mantra_nodes.append(node.node("dusk_effects"))
		if shadow_checkbox > 0:
				mantra_nodes.append(node.node("dusk_shadow"))
			print "Size of mantra_nodes: ", len(mantra_nodes)


	# No valid nodes, display error message
	if (len(mantra_nodes) == 0):
		hou.ui.displayMessage(("Yo, there ain't nothin for me to render!\n\n"
							"Make sure you have selected the layers you would like to render."),   severity=hou.severityType.Warning)
	# Show confirmation dialog
	else:
		dialog = ExportDialog()
		dialog.show()
		pyqt_houdini.exec_(dialog)
