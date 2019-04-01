# We're going to need asset management module
from byuam import Environment, Project

# Minimal UI
from byuminigui.select_from_list import SelectFromList, SelectFromMultipleLists
from byuminigui.write_message import WriteMessage

class GeneralPrompts(object):
    '''
        Here's a bunch of useful method/handler pairs you can instance as you build tools.
    '''
    def SelectElementDialog(self, parent=None, filter=None):
        title = "Select element:"

        if filter:
            lists = Project().list_bodies_by_departments(filter)
        else:
            lists = Project().list_bodies_by_departments()

        self.selectFromMultipleLists = SelectFromMultipleLists(parent, title, lists)
        return self.selectFromMultipleLists

    def submitted_element(self, results):
        department, bodies = results
        body = Project().get_body(bodies[0])
        element = body.get_element(department)

        self.data.update({
            "body": body,
            "element" : element
        })

    def CommitMessageDialog(self):
        self.writeMessage = WriteMessage(title="Write commit message:")
        return self.writeMessage

    @Slot(str)
    def submitted_commit_message(self, message):
        self.data.update({"message" : message})
        self.do_next_gui_method()

    '''
        Display a gui or non-gui safe error message
    '''
    def display_message(self, message, details="", gui=True):
        if not gui:
            byuminigui.quick_dialogs.info(message, details)
        else:
            print message
            print "Details:\n\t{0}".format(details)
