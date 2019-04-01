from byuam import *
from byuminigui import quick_dialogs
import pymel.core as pm

import json

from maya_exporter import MayaExporter

import maya_utils

class JSONExporter(MayaExporter, object):
    def __init__(self, gui=True, element=None, show_tagger=False):
        MayaExporter.__init__(self, gui=gui, element=element, show_tagger=show_tagger)

    def insert_gui_methods_first(self):
        super(JSONExporter, self).insert_gui_methods_first()

    def insert_gui_methods_middle(self):
        super(JSONExporter, self).insert_gui_methods_middle()

    def insert_gui_methods_last(self):
        super(JSONExporter, self).insert_gui_methods_last()

    def append_gui_methods_after(self):
        super(JSONExporter, self).append_gui_methods_after()

    def export_prop(self):
        prop_node = maya_utils.get_top_level_nodes()[0]
        json_cache_dir = self.json_cache_dir(self.body)
        name = self.body.get_name()
        version_number = 0
        json_data = self.prop_JSON_data(prop_node, name, version_number)
        json_cache_filepath = os.path.join(json_cache_dir, self.json_filename(name, version_number))
        with open(json_cache_filepath, "w") as f:
            f.write(json.dumps(json_data))
            f.close()

    def export_char(self):
        if self.publish_data["gui"]:
            quick_dialogs.warning("Exporting JSON files for static characters is not supported at this time.")
        else:
            print "{0} is a character. No JSON was exported.".format(self.body.get_name())

    def export_set(self):
        json_cache_dir = self.json_cache_dir(self.body)
        references = maya_utils.get_loaded_references()
        set_json_data = []
        for ref in references:
            prop_node = maya_utils.get_root_node_from_reference(ref)
            name, version_number = maya.extract_reference_data(ref)
            prop_json_data = self.prop_JSON_data(prop_node, name, version_number)
            set_json_data.append(prop_json_data)
        json_cache_filepath = os.path.join(json_cache_dir, "whole_set.json")
        with open(json_cache_filepath, "w") as f:
            f.write(json.dumps(json_cache_filepath))
            f.close()

    def export_shot(self):
        json_cache_dir = self.json_cache_dir(self.body)
        references = maya_utils.get_loaded_references()
        sets_json_data = []
        chars_json_data = []
        props_json_data = []
        project = Project()
        for ref in references:
            node = maya_utils.get_root_node_from_reference(ref)
            name, version_number = maya.extract_reference_data(ref)
            reference_body = project.get_body(name)
            if not reference_body or not reference_body.is_asset():
                continue
            if reference_body.get_type() == AssetType.SET and not maya_utils.has_parent_set(node):
                sets_json_data.append(self.general_JSON_data(name, version_number))
            elif reference_body.get_type() == AssetType.CHARACTER and maya_utils.children_tagged_with_flag(node, ExportFlags.EXPORT):
                chars_json_data.append(self.general_JSON_data(name, version_number))
            elif reference_body.get_type() == AssetType.PROP and maya_utils.children_tagged_with_flag(node, ExportFlags.EXPORT):
                props_json_data.append(self.prop_JSON_data(node, name, version_number))
        sets_json_cache_filepath = os.path.join(json_cache_dir, "sets.json")
        chars_json_cache_filepath = os.path.join(json_cache_dir, "characters.json")
        props_json_cache_filepath = os.path.join(json_cache_dir, "animated_props.json")

        with open(sets_json_cache_filepath, "w") as f:
            f.write(sets_json_data)
            f.close()
        with open(chars_json_cache_filepath, "w") as f:
            f.write(chars_json_data)
            f.close()
        with open(props_json_cache_filepath, "w") as f:
            f.write(props_json_data)
            f.close()

    def general_JSON_data(self, name, version_number):
        return {
            "asset_name" : name,
            "version_number" : version_number,
            }

    def prop_JSON_data(self, root_node, name, version_number):
        mesh = maya_utils.find_first_mesh(root_node)
        json_data = self.general_JSON_data(name, version_number)
        json_data.update(maya_utils.get_anchor_points(mesh))
        return json_data

    def json_cache_dir(self):
        element = self.body.get_element(Department.MODEL)
        filepath = os.path.join(Project().get_assets_dir(), element.get_cache_dir)
        return filepath

    def json_filename(name, version_number):
        return name + "_" + str(version_number) + ".json"
