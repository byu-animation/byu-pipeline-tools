import os

# Other export scripts
import maya_utils
from alembic_exporter_v2 import AlembicExporter
from json_exporter_v2 import JSONExporter

# We're going to need asset management module
from byuam import Environment, Project

# Minimal UI
from byuminigui.checkbox_options import CheckBoxOptions
from byuminigui.select_from_list import SelectFromList

# Import BYU Tools
from byutools.publisher import Publisher

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.QtCore import Slot


'''
    Works as a publisher, but adds an additional scene prep dialog at the beginning,
    and runs the Maya export scripts at the end.
'''
class MayaPublisher(Publisher):

    def __init__(self, gui=True, src=None):
        super(MayaPublisher, self).__init__(gui, src)

    def get_src_file(self):
        filename, untitled = maya_utils.get_scene_file()
        if untitled:
            return maya_utils.save_scene_file()
        else:
            return maya_utils.get_scene_file()[0]

    def insert_gui_methods_first(self):
        super(JSONExporter, self).insert_gui_methods_first()
        self.gui_methods = [
            (self.ScenePrepDialog, self.submitted_scene_prep)
        ] + self.gui_methods

    def insert_gui_methods_middle(self):
        super(JSONExporter, self).insert_gui_methods_middle()

    def insert_gui_methods_last(self):
        super(JSONExporter, self).insert_gui_methods_last()

    def append_gui_methods_after(self):
        super(JSONExporter, self).append_gui_methods_after()

    '''
        Step 0: A non-gui way of doing this.
    '''
    def non_gui_publish(self):
        self.data.update({
            "clear_construction_history" : False,
            "freeze_transformations" : False,
            "delete_image_planes" : False,
            "group_top_level" : True,
            "convert_to_education" : True
        })
        super(MayaPublisher, self).non_gui_publish(self)

    '''
        Step 1: ScenePrepDialog() -> submitted_scene_prep
        Defined in maya-tools.MayaPrompts
    '''

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
            self.display_error("Problems preparing scene {0}".format(self.publish_data["src"], details=str(e)))

        else:
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
        print "Finished publish with the following data:"
        print self.data
        self.exportAlembic()

    def exportAlembic(self):
        abcExporter = AlembicExporter(gui=self.data["gui"], element=self.data["element"], show_tagger=True)
        abcExporter.export()
        self.exportJSON()

    def alembicExported(self):
        self.do_next_gui_method()

    def exportJSON(self):
        jsonExporter = JSONExporter(gui=self.data["gui"], element=self.data["element"])
        jsonExporter.export()

    def jsonExported(self):
        self.do_next_gui_method()
