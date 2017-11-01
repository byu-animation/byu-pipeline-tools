from PySide2 import QtGui, QtWidgets, QtCore
from TrHttpRPC import TrHttpRPC
import urllib
import datetime
import os
import re
import shutil
import hou
from byugui import message_gui
from byugui.assemble_gui import AssembleWindow
from byuam import Project, Environment

# Creates the dialog box
class ExportDialog(QtWidgets.QWidget):

	finished = QtCore.Signal()

	def __init__(self, parent, renderNodes):
		super(ExportDialog, self).__init__()
		self.parent = parent
		self.project = Project()
		self.environment = Environment()
		self.renderNodes = renderNodes
		self.initUI()

	def initUI(self):
		# Window layout
		self.setFixedSize(360, 420)
		self.setWindowTitle("Confirm Export")
		main_layout = QtWidgets.QVBoxLayout()
		self.setLayout(main_layout)

		# Job Name Input Widget
		self.jobName = QtWidgets.QLineEdit("DeleteMe")
		self.jobName.selectAll()
		name_layout = QtWidgets.QHBoxLayout()
		name_layout.addWidget(QtWidgets.QLabel("Job Name:"))
		name_layout.addWidget(self.jobName)
		main_layout.addLayout(name_layout)

		# Priority and Start Time
		# Priority
		self.priority = QtWidgets.QComboBox()
		priority_opt = ["Very Low", "Low", "Medium", "High", "Very High"]
		for opt in priority_opt:
			self.priority.addItem(opt)
		self.priority.setCurrentIndex(2)
		# Begin time
		self.delay = QtWidgets.QComboBox()
		delay_opts = ["Immediate", "Manual", "Delayed"]
		for opt in delay_opts:
			self.delay.addItem(opt)
		self.delay.currentIndexChanged.connect(self.delaytime)
		# Combo box options layout
		opts_layout = QtWidgets.QHBoxLayout()
		opts_layout.addWidget(QtWidgets.QLabel("Priority:"))
		opts_layout.addWidget(self.priority)
		opts_layout.addWidget(QtWidgets.QLabel("Begin:"))
		opts_layout.addWidget(self.delay)
		opts_layout.addStretch()
		main_layout.addLayout(opts_layout)

		# Time-frame selection for delayed jobs
		self.delay_time = QtWidgets.QLineEdit("5")
		self.delay_unit = QtWidgets.QComboBox()
		delay_unit_opts = ["mins","hours","days"]
		for opt in delay_unit_opts:
			self.delay_unit.addItem(opt)
		self.delay_unit.setCurrentIndex(0)
		# Delay time layout
		self.delay_layout = QtWidgets.QHBoxLayout()
		self.delay_layout.addWidget(QtWidgets.QLabel("Delay time:"))
		self.delay_layout.addWidget(self.delay_time)
		self.delay_layout.addWidget(self.delay_unit)
		self.delay_layout.addStretch()
		self.delaytime(0)
		main_layout.addLayout(self.delay_layout)

		# Mantra node selection list
		self.select = QtWidgets.QListWidget()
		self.select.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		for node in self.renderNodes:
			item = QtWidgets.QListWidgetItem(node.name())
			self.select.addItem(item)
			# must come after adding to widget
			item.setSelected(True)
		main_layout.addWidget(self.select)

		# Buttons
		self.export_btn = QtWidgets.QPushButton('Export')
		self.export_btn.clicked.connect(self.export)
		self.cancel_btn = QtWidgets.QPushButton('Cancel')
		self.cancel_btn.clicked.connect(self.close)
		btn_layout = QtWidgets.QHBoxLayout()
		btn_layout.addWidget(self.cancel_btn)
		btn_layout.addWidget(self.export_btn)
		main_layout.addLayout(btn_layout)


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

		# Get user, project, and time info so we can make a temp folder
		user = self.environment.get_current_username()
		projectName = self.project.get_name()
		time_now = datetime.datetime.now()

		#Make a temp folder for the rib files based on the user and the current time
		ribDir = "/groups/"+projectName+"/ribs/"+user+"_"+time_now.strftime("%m%d%y_%H%M%S")
		print "ribDir", ribDir, " renderNodes size: ", len(self.renderNodes)
		os.makedirs(ribDir)

		# Sanitize job title
		title = re.sub(r'[{}"\']', "", str(self.jobName.text())).strip(' \t\n\r')
		if len(title) == 0:
			title = self.empty_text

		# This is the start of the alfred/tractor script we send to engine
		job_script = "Job -title {"+title+"} -metadata {Spooled by "+user+"} -init {\n\tAssign ribdir {"+ribDir+"}\n} -service {PixarRender} -subtasks {"

		# Loop through each frame of our nodes and create frame tasks and append it to the job script
		for index, node in enumerate(self.renderNodes):
			# Make sure this node was selected for export
			print node.name();
			if self.select.item(index).isSelected():
				name = node.name()
				start = int(node.parm('f1').eval())
				end = int(node.parm('f2').eval())
				step = int(node.parm('f3').eval())
				job_script += "\n\tTask {"+("%s [%d-%d]" % (name, start, end))+"} -subtasks {"

				oldOutputMode = node.parm('rib_outputmode').eval()
				oldDiskFile = node.parm('soho_diskfile').eval()
				# Activate rib output
				node.parm('rib_outputmode').set(True)
				node.parm('soho_diskfile').set(ribDir+('/%s_$F04.rib' % name))

				# Loop through every frame in framerange
				for frame in range(start, end+1, step):
					job_script += "\n\t\tTask {Frame %04d} -cmds { RemoteCmd {/opt/pixar/RenderManProServer-21.3/bin/prman -progress $ribdir/%s_%04d.rib} }" % (frame, name, frame)
					# Render this frame to the ifd file
					node.render([frame, frame])
				job_script += "\n\t}"

				# Restore rib output
				node.parm('soho_outputmode').set(oldOutputMode)
				node.parm('soho_diskfile').set(oldDiskFile)

		job_script += "\n} -cleanup { RemoteCmd {rm -rf "+ribDir+"/} }"

		# Attempt to spool job, with the option to keep trying
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
			shutil.rmtree(ribDir)
		message_gui.info("Job sent to Tractor!")

	# Spool the generated script to the engine
	def spool(self, job_script, time_now):
		print "Spooling"
		delay_type = self.delay.currentIndex()
		# Spool parameters
		spool_url = "spool?"
		# Current user will own this job
		spool_url += "jobOwner=" + urllib.quote("render")
		#TODO Why do we do the render user instead of the current user?? To get the current user use current_user = self.environment.get_current_username()
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

def go(renderNodes):
	# Then show the dialog
	global dialog
	renderNodes = []
	renderNodes.append(hou.node("/out/ris1"))
	dialog = ExportDialog(hou.ui.mainQtWindow(), renderNodes)
	dialog.show()
