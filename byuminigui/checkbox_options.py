try:
    from PySide import QtGui as QtWidgets
    from PySide import QtGui as QtGui
    from PySide import QtCore
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore

from tool_widget import ToolWidget

class CheckBoxOptions(ToolWidget):
    
    options_dict = {}

    def __init__(self, parent=None, title="CheckBox Options", options=[]):
        QtWidgets.QWidget.__init__(self)
        if parent:
            self.parent = parent
        self.setObjectName('CheckBoxOptions')
        self.setWindowTitle(title)
        self.resize(600,150)

        vbox = QtWidgets.QVBoxLayout()

        for option in options:
            self.options_dict[option[1]] = option[2]

            hbox = QtWidgets.QHBoxLayout()
            option_checkbox = QtWidgets.QCheckBox(option[0])
            option_checkbox.setChecked(option[2])
            option_checkbox.clicked.connect(lambda is_checked: self.option_changed(option[1], is_checked))
            hbox.addWidget(option_checkbox)
            vbox.addLayout(hbox)

        self.button = QtWidgets.QPushButton("submit")
        self.button.clicked.connect(self.submit)
        vbox.addWidget(self.button)
        self.setLayout(vbox)
        self.show()

    def option_changed(self, option_key, is_checked):
        self.options_dict.update({option_key : is_checked})

    def submit(self):
        self.submitted.emit(self.options_dict)
        self.close()
