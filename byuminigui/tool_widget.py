try:
    from PySide import QtGui as QtWidgets
    from PySide import QtGui as QtGui
    from PySide import QtCore
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore

class ToolWidget(QtWidgets.QWidget):

    submitted = Signal(object)
    cancelled = Signal()

    def emit_submitted(self, result, close=True):
        self.submitted.emit(result)
        if close:
            self.close()

    def emit_cancelled(self, close=True):
        self.cancelled.emit()
        self.close()
        if close:
            self.close()
