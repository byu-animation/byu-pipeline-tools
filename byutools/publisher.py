import os

# We're going to need asset management module
from byuam import *

# Minimal UI
from byuminigui.select_from_list import SelectFromList, SelectFromMultipleLists
from byuminigui.write_message import WriteMessage

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.Core import Slot

from gui_tool import GUITool

'''
    Executes a series of methods prompting for user input where needed.

    Alternatively, will auto publish if gui is set to False.
'''

class Publisher(GUITool):

    def __init__(self, gui=True, src=None):

        if not src:
            src = self.get_src_file()

        self.data = {
            "gui" : gui,
            "user" : Environment().get_user(),
            "src" : src
        }

    def get_src_file(self):
        raise NotImplementedError("get_src_file() is not implemented.")

    def publish(self):
        directory = os.path.dirname(self.data["src"])
        element = Project().get_checkout_element(directory)

        if element:
            self.data.update({
                "body" : Project().get_body(element.get_parent()),
                "element" : element
            })

        if not self.data["gui"]:
            if "element" in self.data:
                self.auto_publish_element()
            else:
                print "Cannot publish {0}, not checked out.".format(src)
        else:
            self.set_gui_method_order()
            self.do_next_gui_method()

    '''
        We set the steps, in order, that each part of Publish will run.
        Entries with two non-null elements are a Slot/Signal pair.
        The first method must return a QtWidget that has a submitted() signal.
    '''

    def set_gui_method_order(self):

        self.gui_method_number = 0

        self.gui_method_order = [
            (self.prepare_scene, None),
            (self.SelectElementDialog, self.submitted_element),
            (self.CommitMessageDialog, self.submitted_commit_message),
            (self.publish_element, None)
            (self.export, None)
        ]

    '''
        Step 0: A non-gui way of doing this.
    '''

    def auto_publish(self):
        self.prepare_scene()
        self.publish_element()
        self.export()

    '''
        Step 1: Prepare the scene for export, doing whatever is needed.
    '''
    def prepare_scene(self):
        if "element" in self.data:
            self.skip_to_next((self.CommitMessageDialog, self.submitted_commit_message))
        else:
            self.do_next_gui_method()

    '''
        Step 2: SelectElementDialog() -> submitted_element()
        (Defined in the GUITool class)
    '''

    '''
        Step 3: Write a commit message
    '''
    def CommitMessageDialog(self):
        return WriteMessage("Write commit message:")

    @Slot(str)
    def submitted_commit_message(self, message):
        data.update({"message" : message})
        self.do_next_method()

    '''
        Step 4: Publish element
    '''
    def publish_element(self):
        element = self.data["element"]
        user = self.data["user"]
        src = self.data["src"]
        message = self.data["message"]
        element.publish(user, src, message)
        self.do_next_method()

    '''
        Step 5: Export will be implemented in child classes as needed.
    '''
    def export(self):
        print "Finished publish with the following data:"
        print self.data
