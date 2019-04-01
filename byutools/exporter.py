from byuam import Environment, Project

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.QtCore import Slot

from gui_tool import GUITool
from gui_method import GUIMethod

'''
    Executes a series of methods to prompt the user for input about
    a certain element being exported to a cache.

    There's an option to call this from a publisher by passing in the
    publisher that just finished. If that is the case, it will set the
    element equal to the publisher's element.

    Alternatively, will auto-export if gui is set to False.
'''

class Exporter(GUITool):
    def __init__(self, gui=True, element=None):
        super(Exporter, self).__init__(gui=gui)

        if element:
            self.data.update({
                "body" : Project().get_body(element.get_parent()),
                "element" : element
            })

    def export(self):
        if self.gui:
            self.set_gui_methods()

            if "body" in self.data and "element" in self.data:
                self.delete_gui_method(GUIMethod(self.SelectElementDialog, self.submitted_element))

            self.run_gui_methods()

        else:
            self.non_gui_export()

    '''
        Exporter needs a select_element_dialog to come first
    '''
    def insert_gui_methods_first(self):
        super(Exporter, self).insert_gui_methods_first()

        self.gui_methods = [
            GUIMethod(self.SelectElementDialog, self.submitted_element)
        ] + self.gui_methods

    def insert_gui_methods_middle(self):
        super(Exporter, self).insert_gui_methods_middle()

    def insert_gui_methods_last(self):
        super(Exporter, self).insert_gui_methods_last()

        self.gui_methods += [
            GUIMethod(self.export_by_body)
        ]

    '''
        Step 0: a non-gui way of doing this.
    '''
    def non_gui_export(self):
        self.export_by_body()

    '''
        Step 1: SelectElementDialog() -> submitted_element()
        (Defined in the GUITool class)
    '''

    '''
        Step 2 (final): Export by body
    '''
    def export_by_body(self):
        if not "body" in self.data or not "element" in self.data:
            self.display_error("Error with body or element.")
            self.exit_tool(succeeded=False)
            return

        else:
            self.body = self.data["body"]
            self.element = self.data["element"]

        if self.body.is_asset():
            if self.body.get_type() == AssetType.PROP:
                self.export_prop()
            elif self.body.get_type() == AssetType.SET:
                self.export_set()
            elif self.body.get_type() == AssetType.CHARACTER:
                self.export_char()
        else:
            if self.body.is_shot():
                self.export_shot()

    def export_prop(self):
        pass

    def export_char(self):
        pass

    def export_set(self):
        pass

    def export_shot(self):
        pass
