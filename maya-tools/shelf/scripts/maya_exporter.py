from byuam import *
from byuminigui import quick_dialogs
from byutools.exporter import Exporter

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.QtCore import Slot

'''
    Runs after a publisher to export anything that needs exporting.
'''

class MayaExporter(Exporter, MayaPrompts):
    def __init__(self, gui=True, element=None, show_tagger=True):
        super(MayaExporter, self).__init__(gui=gui, element=element)

        self.show_tagger = show_tagger

    def insert_gui_methods_first(self):
        super(MayaExporter, self).insert_gui_methods_first()

    def insert_gui_methods_middle(self):
        super(MayaExporter, self).insert_gui_methods_middle()
        if self.show_tagger:
            self.gui_methods += [
                (self.TaggedItemsDialog, self.submitted_tagged_items)
            ]

    def insert_gui_methods_last(self):
        super(MayaExporter, self).insert_gui_methods_last()

    def append_gui_methods_after(self):
        super(MayaExporter, self).append_gui_methods_after()
