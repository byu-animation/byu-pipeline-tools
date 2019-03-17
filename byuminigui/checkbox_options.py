try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore

class CheckBoxOptions(QtWidgets.QWidget):

    submitted = Signal(dict)
    self.options_dict = {}

    def __init__(self, parent=None, title="CheckBox Options", options=[]):
        super(CheckBoxOptions, self).__init__()
        self.resize(600,1000)

        vbox = QtWidgets.QVBoxLayout()

        for option in options:
            self.options_dict[option[1]] = option[2]

            hbox = QtWidgets.QHBoxLayout()
            option_checkbox = QtGui.QCheckBox(option[0])
            option_checkbox.setChecked(option[2])
            option_checkbox.clicked.connect(lambda is_checked: self.option_changed(option[1], is_checked))
            vbox.addLayout(hbox)

        self.button = QtWidgets.QPushButton("submit")
        self.button.clicked.connect(self.submit)
        vbox.addWidget(self.button)
        self.addLayout(vbox)

    def option_changed(self, option_key, is_checked):
        options_dict.update({option_key : is_checked})

    def submit(self):
        self.submitted.emit(self.options_dict)
