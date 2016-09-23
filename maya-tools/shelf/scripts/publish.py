from byuam import Department
from byugui.publish_gui import PublishWindow
from PyQt4 import QtCore
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip
import alembic_static_exporter
import os

maya_publish_dialog = None

def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

def post_publish():
    element = maya_publish_dialog.result

    if maya_publish_dialog.published:
        if not cmds.file(q=True, sceneName=True) == '':
            cmds.file(save=True, force=True) #save file

        #Publish
        user = maya_publish_dialog.user
        src = maya_publish_dialog.src
        comment = maya_publish_dialog.comment
        dst = element.publish(user, src, comment)
        #Ensure file has correct permissions
        try:
            os.chmod(dst, 0660)
        except:
            pass

        print "TODO: export playblast"
        print maya_publish_dialog.result.get_name()

        if element.get_department() == Department.MODEL:
            print "Exporting Alembic"
            alembic_static_exporter.go()

def go():
    parent = maya_main_window()
    filePath = cmds.file(q=True, sceneName=True)
    global maya_publish_dialog
    maya_publish_dialog = PublishWindow(filePath, parent, [Department.MODEL, Department.RIG, Department.LAYOUT, Department.ANIM])
    maya_publish_dialog.finished.connect(post_publish)
