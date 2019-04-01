try:
    from PySide import QtGui as QtWidgets
    from PySide import QtGui as QtGui
    from PySide import QtCore
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore

class WriteMessage(QtWidgets.QWidget):
    submitted = QtCore.Signal(str)

    def __init__(self, parent=None, title="Write Message"):
        super(WriteMessage, self).__init__()
        self.setWindowTitle(title)
        self.initializeVBox()
        self.setLayout(self.vbox)
        self.show()

    def initializeVBox(self):
        self.vbox = QtWidgets.QVBoxLayout()
        self.initializeMessageField()
        self.initializeSubmitButton()

    def initializeMessageField(self):
        self.message = QtWidgets.QPlainTextEdit()
        self.message.textChanged.connect(self.textChanged)
        self.vbox.addWidget(self.message)

    def initializeSubmitButton(self):
        # Create the button widget
        self.button = QtWidgets.QPushButton("submit")
        self.button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.button.clicked.connect(self.submit)
        self.button.setEnabled(False)
        self.vbox.addWidget(self.button)

    def textChanged(self):
        self.button.setEnabled(len(self.message.toPlainText()) > 0)

    def submit(self):
        self.submitted.emit(self.message.toPlainText())
        self.close()
