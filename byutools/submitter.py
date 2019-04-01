
from gui_tool import GUITool

class Submitter(GUITool):

    def __init__(self, gui=True):
        super(GUITool, self).__init__()

    def set_gui_method_order(self):
        if not self.gui:
            return

    def submit(self):
        pass

    def auto_submit(self):
        pass

    
