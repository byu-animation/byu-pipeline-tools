import os

# Other export scripts
import maya_utils, alembic_exporter, json_exporter

# We're going to need asset management module
from byuam import *

# Minimal UI
from byuminigui.checkbox_options import CheckBoxOptions
from byuminigui import quick_dialogs

# Import BYU Tools
from byutools.publisher import Publisher

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.Core import Slot


'''
    Works as a publisher, but adds an additional scene prep dialog at the beginning,
    and runs the Maya export scripts at the end.
'''
class MayaPublisher(Publisher):

    def __init__(self, gui=True, src=None):
        super(MayaPublisher, self).__init__(gui, src)


    def set_gui_method_order(self):
        # Use the default steps defined in byutools.Publisher
        super(MayaPublisher, self).set_gui_method_order()

        # We insert a scene prep dialog that will run first.
        self.gui_method_order.insert(0, (self.ScenePrepDialog, self.submitted_scene_prep))

    '''
        Step 0: A non-gui way of doing this.
    '''
    def auto_publish(self):
        self.data.update({
            "clear_construction_history" : True,
            "freeze_transformations" : True,
            "delete_image_planes" : True,
            "group_top_level" : True,
            "convert_to_education" : True
        })
        super(MayaPublisher, self).auto_publish()

    '''
        Step 1: Scene prep dialog to ask for settings
    '''
    def ScenePrepDialog(self):

        title = "Scene Cleanup Options"

        options = [
            ("Clear Construction History", "clear_construction_history", True),
            ("Freeze Transformations", "freeze_transformations", True),
            ("Delete Image Planes", "delete_image_planes", True),
            ("Group Top Level", "group_top_level", True),
            ("Conert To Education License", "convert_to_education", True)
        ]

        return CheckBoxOptions(parent=maya_utils.maya_main_window(), title=title, options=options)

    @Slot(list)
    def submitted_scene_prep(self, selections):

        for selection in selections:
            self.publish_data.update({selection[1], selection[2]}})

        self.do_next_gui_method()

    '''
        Step 2: Prepare the scene
    '''
    def prepare_scene(self):

        try:
            if self.data["clear_construction_history"]:
                maya_utils.clear_construction_history()
            if self.data["freeze_transformations"]:
                failed = maya_utils.freeze_transformations()
                print "Freeze transformations failed on: {0}".format(failed)
            if self.data["delete_image_planes"]:
                maya_utils.delete_image_planes()
            if self.data["group_top_level"]:
                maya_utils.group_top_level()
            if self.data["convert_to_education"]:
                maya_utils.convert_to_education()
            maya_utils.save_scene_file()

        except Exception as e:
            self.display_error("Problems preparing scene {0}".format(self.publish_data["src"], details=str(e))
            return False

        self.do_next_gui_method()

    '''
        Step 3: Select an element.
        SelectElementDialog() -> submitted_element()
        (defined in byutools.GUITool)
    '''

    '''
        Step 4: Write a commit message.
        CommitMessageDialog() -> submitted_commit_message()
        (defined in byutools.Publisher)
    '''

    '''
        Step 5: Publish element
        publish_element()
        (defined in byutools.Publisher)
    '''

    '''
        Step 6 (final): Run maya exporters
    '''
    def export(self):
        AlembicExporter(self.publish_data["gui"], self, True).export()
        JsonExporter(self.publish_data["gui"], self).export()
        print "Finished publish with the following data:"
        print self.publish_data
