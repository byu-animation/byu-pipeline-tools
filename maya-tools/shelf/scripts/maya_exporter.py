from byuam import *
from byuminigui import quick_dialogs
from byutools.exporter import Exporter

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.Core import Slot

'''
    Runs after a publisher to export anything that needs exporting.
'''

class MayaExporter(Exporter):
    def __init__(self, publisher=None, gui=True, show_tagger=True):
        super(MayaExporter, self).__init__(publisher, gui)
        self.show_tagger = show_tagger

    def export_shot(self):
        if self.body.is_shot():
            if self.gui and self.show_tagger:
                taggedItemsDialog = TaggedItemsDialog()
                taggedItemsDialog.submitted.connect(self.submitted_tagged_items)
        pass

    def TaggedItemsDialog(self):
        title = "Tag or untag references here"
        self.items = {}
        for reference, node in maya_utils.get_references_as_node_dict():
            self.items[reference] = any_children_are_tagged(node)
        taggedItemsDialog = CheckBoxOptions(self.items)
        return taggedItemsDialog

    @Slot(dict)
    def submitted_tagged_items(self, tagged_items):
        node_dict = maya_utils.get_references_as_node_dict()
        self.items.update(tagged_items)
        for item, tagged in tagged_items:
            if tagged:
                maya_utils.tag_node_with_flag(node_dict[item], ExportFlags.EXPORT)
            else:
                maya_utils.untag_node_with_flag(node_dict[item], ExportFlags.EXPORT)
        self.export_shot()
