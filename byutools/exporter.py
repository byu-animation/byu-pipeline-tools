from byuam import *

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.Core import Slot

from gui_tool import GUITool

'''
    Executes a series of methods to prompt the user for input about
    a certain element being exported to a cache.

    There's an option to call this from a publisher by passing in the
    publisher that just finished. If that is the case, it will set the
    element equal to the publisher's element.

    Alternatively, will auto-export if gui is set to False.
'''

class Exporter(GUITool):
    def __init__(self, gui=True, element=None, publisher=None):
        self.publisher = publisher
        self.gui = gui
        self.data = {
            "gui" : self.gui
        }
        if element:
            self.data["body"] = Project().get_body(element.get_parent())
            self.data["element"] = element
        elif publisher:
            self.data["body"] = publisher.data["body"]
            self.data["element"] = publisher.data["element"]

    def export(self):
        self.set_gui_method_order()
        if "body" in self.data and "element" in self.data:
            self.skip_to_next((self.export_by_body, None))
        else:
            self.do_next_gui_method()

    '''
        We set the steps, in order, that each part of Exporter will run.
        Entries with two non-null elements are a Slot/Signal pair.
        The first method must return a QtWidget that has a submitted() signal.
    '''
    def set_gui_method_order(self):
        if not self.gui:
            return

        self.gui_method_number = 0

        self.gui_method_order = [
            (self.SelectElementDialog, self.submitted_element)
            (self.export_by_body, None)
        ]

    '''
        Step 0: a non-gui way of doing this.
    '''
    def auto_export(self):
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
            return
        else:
            self.body = self.data["body"]
            self.element = self.element["element"]
        if self.body.is_asset():
            if self.body.asset_type() == AssetType.PROP:
                export_prop()
            elif self.body.asset_type() == AssetType.SET:
                export_set()
            elif self.body.asset_type() == AssetType.CHARACTER:
                export_char()
        else:
            if self.body.is_shot():
                export_shot()

    def export_prop(self):
        pass

    def export_char(self):
        pass

    def export_set(self):
        pass

    def export_shot(self):
        pass
