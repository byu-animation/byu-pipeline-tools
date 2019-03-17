import os

# We're going to need asset management module
from byuam import *

# Minimal UI
from byuminigui.select_from_list import SelectFromList, SelectFromMultipleLists
from byuminigui.write_message import WriteMessage
from byuminigui import quick_dialogs

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.Core import Slot

'''
    Executes a series of methods prompting for user input where needed.
'''

class GUITool:
    def __init__(self, gui=True):
        self.gui = gui
        pass

    '''
        We set the steps, in order, that each part of the tool will run.
        Entries with two non-null elements are a Slot/Signal pair.
        The first method must return a QtWidget that has a submitted() signal.
    '''
    def set_gui_method_order(self):
        if not self.gui:
            return

        # Examples of what should be here.
        self.gui_method_number = 0 # Always initialize to 0, will increment
        self.gui_method_order = [
            ("this is a standalone method", None),
            ("this method returns a QtWidget", "this is a Slot")
        ]

        raise NotImplementedError("You must implement set_gui_method_order().")

    '''
        Does the next method in the gui_method_order list
    '''
    def do_next_gui_method(self):
        if not self.gui:
            return

        self.method_number += 1
        if self.method_number > len(self.gui_method_order):
            return

        method, handler = self.method_order[self.method_number]
        if handler:
            window_instance = method()
            window_instance.submitted.connect(handler)
            window_instance.show()
            return

    '''
        Skips ahead in the gui_method_order list.
        The -1 is necessary because do_next_gui_method will increment by 1.
    '''
    def skip_to_next(self, method_pair):
        if not self.gui:
            return

        self.method_number = self.method_order[self.method_number:].indexof(method_pair) - 1
        self.do_next_gui_method()

    '''
        Here's a bunch of useful prompts you can instance as you build tools.
    '''

    def SelectElementDialog(self):
        title = "Select element:"
        lists = Project().list_bodies_by_departments()
        window = maya_utils.maya_main_window()
        return SelectFromMultipleLists(title, lists, window)

    @Slot(object)
    def submitted_element(self, element_tuple):
        department, body = element_tuple
        body = Project().get_body(body_name)
        element = body.get_element(department)
        self.data.update({
            "body": body,
            "element" : element
        })
        self.do_next_method()

    '''
        Display a gui or non-gui safe error message
    '''
    def display_error(self, message, details=""):
        if not self.gui:
            quick_dialogs.error(message, details)
        else:
            print message
            print "Details:\n\t{0}".format(details)
