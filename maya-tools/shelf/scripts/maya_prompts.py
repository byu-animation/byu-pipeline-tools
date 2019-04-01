# We're going to need asset management module
from byuam import Environment, Project

# Minimal UI
from byuminigui.select_from_list import SelectFromList, SelectFromMultipleLists
from byuminigui.write_message import WriteMessage

import maya_utils

class MayaPrompts(object):
    def TaggedItemsDialog(self):
        title = "Tag or untag references here"
        items = {}
        for reference, node in maya_utils.get_references_as_node_dict():
            items[reference] = maya_utils.children_tagged_with_flag(node, ExportFlags.ANIMATED)
        taggedItemsDialog = CheckBoxOptions(title, items)
        return taggedItemsDialog

    @Slot(dict)
    def submitted_tagged_items(self, tagged_items):
        references_in_scene = maya_utils.get_references_as_node_dict()
        for name, tagged in tagged_items:
            current_reference = references_in_scene[name]
            is_already_tagged =  maya_utils.children_tagged_with_flag(current_reference, ExportFlags.ANIMATED)
            if tagged and not is_already_tagged:
                maya_utils.tag_node_with_flag(current_reference, ExportFlags.ANIMATED)
            elif is_already_tagged:
                maya_utils.untag_node_with_flag(current_reference, ExportFlags.ANIMATED)
        self.do_next_gui_method()
    
    def ScenePrepDialog(self):

        title = "Scene Cleanup Options"

        options = [
            ("Clear Construction History", "clear_construction_history", False),
            ("Freeze Transformations", "freeze_transformations", False),
            ("Delete Image Planes", "delete_image_planes", False),
            ("Group Top Level", "group_top_level", True),
            ("Convert To Education License", "convert_to_education", True)
        ]

        self.checkBoxOptions = CheckBoxOptions(title=title, options=options)
        return self.checkBoxOptions

    @Slot(object)
    def submitted_scene_prep(self, selections):

        self.data.update(selections)
        self.do_next_gui_method()
