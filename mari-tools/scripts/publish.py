# Author: Ben DeMann

from byuam import Department, Environment
from byugui.publish_gui import PublishWindow
from byugui import message_gui
from PySide import QtGui
import os
import mari
import export_images

mari_publish_dialog = None

def go():
	parent = QtGui.QApplication.activeWindow()
	project_name = mari.projects.current().name() #get the name of the current project
	global mari_publish_dialog
	mari_publish_dialog = PublishWindow(project_name, parent, [Department.TEXTURE])
	mari_publish_dialog.finished.connect(post_publish)

def post_publish():
	element = mari_publish_dialog.result

	if mari_publish_dialog.published:
		#save the file
		project = mari.projects.current()
		project_id = project.uuid()
		export_images.go()
		project.save()
		project.close()

		#Publish
		user = mari_publish_dialog.user
		src = mari_publish_dialog.src
		comment = mari_publish_dialog.comment
		env = Environment()
		user_dir = env.get_user_workspace()

		archive_file = os.path.join(user_dir, str(src) + ".mra")
		mari.projects.archive(project_id, archive_file)

		dst = element.publish(user, archive_file, comment)
		#Ensure file has correct permissions
		try:
			os.chmod(dst, 0660)
		except:
			pass

		#Delete Temp file
		try:
			os.remove(archive_file)
		except:
			print "There was an error while removing the temp file."
			pass

		remove = message_gui.yes_or_no("The Mari Project is safely published. Would you like to remove the project from your Mari cache?")

		if remove:
			mari.projects.remove(project_id)
