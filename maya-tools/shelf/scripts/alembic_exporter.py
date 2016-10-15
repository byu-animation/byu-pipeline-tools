from PyQt4.QtCore import *
from PyQt4.QtGui import *

import maya.cmds as cmds
import maya.OpenMayaUI as omu
from pymel.core import *
# import utilities as amu #asset manager utilities
import os
import sip
import byuam
from byuam.environment import Environment
from byuam.project import Project

WINDOW_WIDTH = 330
WINDOW_HEIGHT = 300

def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QObject)

class AlembicExportDialog(QDialog):
    def __init__(self, parent=maya_main_window()):
    #def setup(self, parent):
        QDialog.__init__(self, parent)
        self.saveFile()
        self.setWindowTitle('Select Objects for Export')
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.create_layout()
        self.create_connections()
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

    def create_connections(self):
        #Connect the buttons
        self.connect(self.export_button, SIGNAL('clicked()'), self.export_alembic)
        self.connect(self.cancel_button, SIGNAL('clicked()'), self.close_dialog)

    def create_export_list(self):
        #Remove all items from the list before repopulating
        self.selection_list.clear()

        #Add the list to select from
        loadedRef = self.getLoadedReferences()

        for ref in loadedRef:
            item = QListWidgetItem(ref)
            item.setText(ref)
            self.selection_list.addItem(item)

        self.selection_list.sortItems(0)

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
        return os.path.basename(refPath).split('.')[0] + '.abc'

    def export_alembic(self):
        self.saveFile()

        selectedReferences = []
        selectedItems = self.selection_list.selectedItems()
        for item in selectedItems:
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
            abcFilePath = elem.get_cache_dir()

            for ref in selectedReferences:
                refAbcFilePath = os.path.join(abcFilePath, self.get_filename_for_reference(ref))
                print "abcFilePath", refAbcFilePath
                command = self.build_alembic_command(ref, refAbcFilePath)
                print "Export Alembic command: ", command
                Mel.eval(command)
                os.system('chmod 774 ' + refAbcFilePath)

        self.close_dialog()

    def saveFile(self):
        if not cmds.file(q=True, sceneName=True) == '':
            cmds.file(save=True, force=True) #save file

    def showConfirmAlembicDialog(self, references):
        return cmds.confirmDialog( title         = 'Export Alembic'
                                 , message       = 'Export Alembic for:\n' + str(references)
                                 , button        = ['Yes', 'No']
                                 , defaultButton = 'Yes'
                                 , cancelButton  = 'No'
                                 , dismissString = 'No')

    def build_alembic_command(self, ref, abcfilepath):
        # First check and see if the reference has a tagged node on it.
        tagged = self.get_tagged_node(ref)

        if tagged == "":
            return ""

		# Then we get the dependencies of that item to be tagged.
        depList = self.get_dependencies(ref)

		# This determines the pieces that are going to be exported via alembic.
        roots_string = ""
        print "tagged: "
        print tagged

		# Each of these should be in a list, so it should know how many to add the -root tag to the alembic.
        for alem_obj in tagged:
            print "alem_obj: " + alem_obj
            roots_string += (" -root %s"%(alem_obj))
		# roots_string = " ".join([roots_string, "-root %s"%(' '.join(tagged))])
        print "roots_string: " + roots_string

        # Commented out 10/16/16: Testing to see if dependency list is necessary in export. Currently there are parenting/ancestor relationship conflicts - Trevor Barrus
		# But it seems we add the dependencies to the thing being exported.
        #for dep in depList:
        #    depRef = ls(dep)
        #    if len(depRef) > 0:
        #        tagged = self.get_tagged_node(depRef[0]).name()
        #    else:
        #        tagged = dep[:-2]

        #    roots_string = " ".join([roots_string, "-root %s"%(tagged)])

        start_frame = cmds.playbackOptions(q=1, animationStartTime=True) - 5
        end_frame = cmds.playbackOptions(q=1, animationEndTime=True) + 5

		# Then here is the actual Alembic Export command for Mel.
        command = 'AbcExport -j "%s -frameRange %s %s -step 0.25 -writeVisibility -noNormals -uvWrite -worldSpace -file %s"'%(roots_string, str(start_frame), str(end_frame), abcfilepath)
        return command

    def get_tagged_node(self, ref):
        # Looks for a tagged node that has the BYU Alembic Export flag on it.
        refNodes = cmds.referenceQuery(unicode(ref), nodes=True)
        rootNode = ls(refNodes[0])
        taggedNode = []
        if rootNode[0].hasAttr("BYU_Alembic_Export_Flag"):
            # taggedNode = rootNode[0]
            taggedNode.append(rootNode[0])
        else:
            # Otherwise get the tagged node that is in the children.
            taggedNode = self.get_tagged_children(rootNode[0])

        if not taggedNode:
            self.showNoTagFoundDialog(unicode(ref))
            return ""

        print "taggedNode ", taggedNode
        return taggedNode

    def get_tagged_children(self, node):
		# Too bad this is similar to the get_tagged_node method. Maybe this could be combined...
		# This needs to grab multiple pieces of geometry - currently this only grabs one.
		# Can we export multiple pieces of geometry? Usually it's been a little different since the mesh is in one place,
		# but it might be good to set it up so that geo in multiple places can be grabbed.
        tagged_children = []
		# for child in node.listRelatives(c=True):
		# 	if child.hasAttr("BYU_Alembic_Export_Flag"):
		# 		return child
		# 	else:
		# 		taggedChild = self.get_tagged_children(child)
		# 		if taggedChild != "":
		# 			return taggedChild
		# return ""
        for child in node.listRelatives(c=True):
            if child.hasAttr("BYU_Alembic_Export_Flag"):
				# print "tagged child: "
				# print child
                tagged_children.append(str(child))
            else:
                taggedChild = self.get_tagged_children(child)
				# if taggedChild != "":
                if taggedChild: # Check if the list is empty
					# print "tagged children: "
					# print taggedChild
					# return taggedChild
					# If ther child below has any elements in the list, then we need to add then here...
					# We need to add them one at a time, and somehow check for uniqueness.
                    for tag in taggedChild:
                        tagged_children.append(tag)
		# print "tagged children: "
		# print tagged_children
        return tagged_children

    def get_dependencies(self, ref):
		# Looks like the
        refNodes = cmds.referenceQuery(unicode(ref), nodes=True)
        rootNode = ls(refNodes[0])
        depList = self.get_dependent_children(rootNode[0])

        return depList

    def get_dependent_children(self, node):
        depList = []
        for const in node.listRelatives(ad=True, type="parentConstraint"):
            par = const.listRelatives(p=True)
            constNS = par[0].split(':')[0]
            targetList = cmds.parentConstraint(unicode(const), q=True, tl=True)
            targetNS = targetList[0].split(':')[0]
            if constNS != targetNS and targetNS not in depList:
                depList.append(targetNS + 'RN')

        print 'depList: ', depList
        return depList

    def showNoTagFoundDialog(self, ref):
        return cmds.confirmDialog( title         = 'No Alembic Tag Found'
                                 , message       = 'Unable to locate Alembic Export tag for ' + ref + '.'
                                 , button        = ['OK']
                                 , defaultButton = 'OK'
                                 , cancelButton  = 'OK'
                                 , dismissString = 'OK')

    def close_dialog(self):
        self.close()

def go():
    dialog = AlembicExportDialog()
    dialog.show()

if __name__ == '__main__':
    go()
