try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore

class CheckBoxOptions(QtWidgets.QWidget):
    def __init__(self, parent=None, title="CheckBox Options", options=[]):
        super(CheckBoxOptions, self).__init__()
        self.resize(600,1000)

        vbox = QtWidgets.QVBoxLayout()

        for option in options:
            hbox = QtWidgets.QHBoxLayout()
            option_checkbox = QtGui.QCheckBox(option[0])
            option_checkbox.setChecked(option[2])
            option_checkbox.clicked.connect(lambda bool: )
            vbox.addLayout(hbox)

        self.addLayout(vbox)

    def options_changed(self, )
