import os

# We're going to need asset management module
from byuam import Environment, Project

try:
    from PySide.QtCore import Slot
except ImportError:
    from PySide2.QtCore import Slot

from gui_tool import GUITool
from gui_method import GUIMethod

'''
    Executes a series of methods prompting for user input where needed.
    Alternatively, will auto publish if gui is set to False.
'''

class Publisher(GUITool):

    def __init__(self, gui=True, src=None):

        super(Publisher, self).__init__(gui=gui)

        if not src:
            src = self.get_src_file()

        self.data.update({
            "tool" : "Publisher",
            "user" : Environment().get_current_username(),
            "src" : src
        })

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

        if self.gui:
            self.set_gui_methods()
            self.run_gui_methods()

        else:
            if "element" in self.data:
                self.non_gui_publish()
            else:
                self.display_error("Cannot publish {0}, not checked out.".format(src))
                self.exit_tool(succeeded=False)

    '''
        We insert prepare_scene(), SelectElementDialog() and CommitMessageDialog()
        at the beginning of the gui_methods, to be run immediately after before_gui_methods()
    '''

    def insert_gui_methods_first(self):
        super(Publisher, self).insert_gui_methods_first()
        self.gui_methods = [
            GUIMethod(self.prepare_scene),
            GUIMethod(self.SelectElementDialog, handler=self.submitted_element),
            GUIMethod(self.CommitMessageDialog, handler=self.submitted_commit_message)
        ] + self.gui_methods

    '''
        We call the super, in case it has anything to insert in the middle. We, however,
        do not.
    '''

    def insert_gui_methods_middle(self):
        super(Publisher, self).insert_gui_methods_middle()

    '''
        We insert GUI Methods at the end, to be run right before after_gui_methods()
    '''

    def insert_gui_methods_last(self):
        super(Publisher, self).insert_gui_methods_last()
        self.gui_methods += [
            GUIMethod(self.publish_element)
        ]

    '''
        Step 0: A non-gui way of doing this.
    '''

    def non_gui_publish(self):
        self.prepare_scene()
        self.publish_element()

    '''
        Step 1: Prepare the scene for export, doing whatever is needed.
    '''
    def prepare_scene(self):
        if "element" in self.data:
            self.skip_to_next(GUIMethod(self.CommitMessageDialog, self.submitted_element))

    '''
        Step 2: SelectElementDialog() -> submitted_element()
        (Defined in the byutools.GeneralPrompts class)
    '''

    '''
        Step 3: CommitMessageDialog() -> submitted_commit_message()
        (Defined in byutools.GeneralPrompts class)
    '''

    '''
        Step 4: Publish element
    '''
    def publish_element(self):
        element = self.data["element"]
        user = self.data["user"]
        src = self.data["src"]
        message = self.data["message"]
        element.publish(user, src, message)
