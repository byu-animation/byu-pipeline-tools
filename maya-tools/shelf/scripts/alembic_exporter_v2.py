from byuam import *
from byugui import message_gui
import os
import pymel.core as pm

from maya_exporter import MayaExporter

import maya_utils
from maya_utils import ExportFlags


class AlembicExporter(MayaExporter, object):
    def __init__(self, gui=True, element=None, show_tagger=False):
        super(AlembicExporter, self).__init__(gui=gui, element=element, show_tagger=show_tagger)
        #self.as_super = super(AlembicExporter, self)
        #self.as_super.__init__(publisher, gui)
        pm.loadPlugin('AbcExport')

    def export_prop(self):
        pass
        #for top_level_node in get_top_level_nodes():

        #abc_file_path = self.abc_file_path(name)

    def export_char(self):
        pass
        #abc_file_path = self.abc_file_path(name)

    def export_set(self):
        pass

    def export_shot(self):
        abc_cache_dir = self.abc_cache_dir(asset=False)
        abc_file_path = os.path.join(abc_cache_dir, self.body.get_name)
        refs = maya_utils.get_loaded_references()
        for ref in refs:
            body = maya_utils.get_body_from_reference(ref)
            node = maya_utils.get_root_node_from_reference(ref)
            name, version_number = maya_utils.extract_reference_data(ref)
            if maya_utils.node_is_tagged_with_flag(node, ExportFlags.EXPORT):
                if body.get_type() == AssetType.CHARACTER:
                    export_target = maya_utils.get_first_child_with_flag(node, ExportFlags.EXPORT_TARGET)
                    if export_target:
                        self.export_abc(self.abc_options_default(export_target, abc_cache_dir))

    def export_abc(self, alembic_options):
        command = "AbcExport "
        for option in alembic_options:
            command += option
            if alembic_options[option]:
                if isinstance(alembic_options[option], list):
                    command += " ".join(list)
                else:
                    command += str(alembic_options[option])
            command += " "
        pm.Mel(command)

    def abc_options_default(self, root, path):
        start_frame = pm.playbackOptions(q=True, animationStartTime=True)
        end_frame = pm.playbackOptions(q=True, animationStartTime=True)
        step = 0.25
        return {
                "-j" : None,
                "-root" : root,
                "-frameRange" : [start_frame, end_frame],
                "-stripNamespaces" : None,
                "-step" : step,
                "-writeVisiblility" : None,
                "-noNormals" : None,
                "-uvWrite" : None,
                "-worldSpace" : None,
                "-autoSubd" : None,
                "-file" : path
            }

    def abc_options_anim(self, root, path):
        return self.default_alembic_options(root, path)

    def abc_options_static(self, root, path):
        options = self.default_alembic_options(root, path)
        options.update({
            "-frameRange" : [1, 1]
        })
        del options["-step"]
        return options

    def abc_file_path(self, name, version_number=None):
        filename = name + "_main"
        if version_number is not None:
            filename += str(version_number)
        filename += ".abc"
        return os.path.join(self.element.get_cache_dir(), filename)
