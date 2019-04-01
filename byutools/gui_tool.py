import os

# We're going to need asset management module
from byuam import Environment, Project

global non_gui_override
non_gui_override = False

try:
    from PySide.QtCore import Signal
except ImportError:
    try:
        from PySide2.QtCore import Signal
    except:
        non_gui_override = True

from prompts import Prompts

'''
    Executes a series of methods prompting for user input where needed.
'''
class GUITool(object, GeneralPrompts):

    def __init__(self, gui=True):
        super(GUITool, self).__init__()

        self.gui = False if non_gui_override else gui

        self.data = {
            "gui" : gui
        }

        self.exit = False

        if self.gui:
            self.submitted = Signal(object)
            self.cancelled = Signal(object)
            self.gui_method_number = 0
            self.gui_methods = []

    '''
        We set the steps, in order, that each part of the tool will run.
        Entries with two non-null elements are a Signal + Slot pair.
        The first method must return a QtWidget that has a submitted() signal.
    '''
    def set_gui_methods(self):
        if not self.gui:
            raise TriedMethodFromNonGUI("set_gui_methods()")

        self.insert_gui_methods_first()
        self.insert_gui_methods_middle()
        self.insert_gui_methods_last()

        # Start and exit must be inserted always
        self.gui_methods.insert(0, GUIMethod(self.before_gui_methods))
        self.gui_methods.append(GUIMethod(self.after_gui_methods))

    def insert_gui_methods_first(self):
        raise NotImplementedError("insert_gui_methods_first() is not implemented.")

    def insert_gui_methods_middle(self):
        raise NotImplementedError("insert_gui_methods_middle() is not implemented.")

    def insert_gui_methods_last(self):
        raise NotImplementedError("insert_gui_methods_last() is not implemented.")

    '''
        Do not override
    '''
    def before_gui_methods(self):
        self.display_message("Tool started:", str(self.data), gui=False)

    def after_gui_methods(self):
        self.display_message("Tool ended:", str(self.data), gui=False)
        self.exit_gui_methods(succeeded=True)

    '''
        Do not override
    '''

    def run_gui_methods(self):
        self.next_gui_method()

    def exit_tool(self, succeeded=True):
        self.exit = True
        if succeeded:
            self.display_message("Tool succeeded:", str(self.data), gui=False)
            if self.gui:
                self.submitted.emit()
        else:
            self.display_message("Tool failed:", str(self.data), gui=False)
            if self.gui:
                self.cancelled.emit()


    '''
        Does the next method in the gui_method_order list
    '''
    def next_gui_method(self):
        if not self.gui:
            raise TriedMethodFromNonGUI("next_gui_method()")

        if self.exit:
            return

        if self.gui_method_number > len(self.gui_methods):
            raise GUIMethodOutsideBounds(self.gui_method_number, None, self.str_gui_methods)

        method = self.gui_methods[self.gui_method_number]
        # I have to increment here before the gui method gets called.
        self.gui_method_number += 1
        method.run()

        self.next_gui_method()

    '''
        Deletes a method, effectively skipping it
    '''
    def delete_gui_method(self, gui_method):
        self.gui_methods.delete(gui_method)

    '''
        Skips ahead in the gui_methods list.
    '''
    def skip_to_next(self, next_method):
        if not self.gui:
            raise TriedMethodFromNonGUI("next_gui_method()")

        if self.gui_method_number > len(self.gui_methods):
            raise GUIMethodOutsideBounds(self.gui_method_number, next_method, self.str_gui_methods()))
            return

        location = -1
        for i, gui_method in self.gui_methods[self.gui_method_number:]:
            if gui_method == next_method:
                location = i + gui_method_number
                break

        if location == -1 or location > len(self.gui_methods):
            raise GUIMethodOutsideBounds(self.gui_method_number, next_method, self.str_gui_methods()))

        self.gui_method_number = i

    def str_gui_methods(self):
        result = ""
        for gui_method in self.gui_methods:
            if gui_method.handler:
                result += "\n{0}() -> {1}()".format(gui_method.method.__name__, gui_method.handler.__name__)
            else:
                result += "\n{0}()".format(gui_method.method.__name__)
        return result


    class TriedMethodFromNonGUI(Exception):
        def __init__(self, method_name):
            super(TriedMethodFromNonGUI, self).__init__(self, method_name)

    class GUIMethodOutsideIndex(Exception):
        def __init__(self, gui_method, gui_methods):
            super(GUIMethodOutsideBounds, self).__init__(self, "Index: " + str(index) + "\nMethod: " + str(gui_method) + "\nGUI Methods:\n" + gui_methods)
