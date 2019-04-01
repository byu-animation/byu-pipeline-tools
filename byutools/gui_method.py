'''
    A method that includes a GUI
'''

class GUIMethod(object):
    finished = Signal()

    def __init__(self, method, handler=None):
        self.method = method
        self.handler = handler

    def run():
        if self.handler:
            toolWidget = method()
            toolWidget.succeeded.connect(handler)
            toolWidget.cancelled.connect(self.finished)
        else:
            method()

    def __eq__(self, other):
        methods_match = self.method.__name__ == other.method.__name__
        handlers_match = True if not self.handler and not other.handler else self.handler.__name__ == other.handler.__name__
        return methods_match and handlers_match

    def __str__(self):
        result = "GUIMethod"
        result = "\n\tMethod: " + self.method.__name__
        result += "\n\tHandler: " + self.handler.__name__ if self.handler else "None"
        return result
