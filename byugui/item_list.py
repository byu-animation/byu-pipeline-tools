try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore

class SelectFromList(QtWidgets.QWidget):
    selected_list = QtCore.Signal(list)
    selected = QtCore.Signal(str)
    value = ""
    values = []

    allItems = []
    shownItems = []

    def __init__(self, parent=None, multiple_selection=False):
        super(SelectFromList, self).__init__()

        self.resize(600,600)

        self.multiple_selection = multiple_selection
        self.setObjectName('SelectFromList')
        vbox = QtWidgets.QVBoxLayout()

        # If it's single selection, bring in the searchbox
        if not multiple_selection:
            hbox = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel("Refine Search: ")
            hbox.addWidget(label)
            self.searchBox = QtWidgets.QLineEdit()
            self.searchBox.textEdited.connect(self.textEdited)
            self.searchBox.setStyleSheet("color: white")
            self.searchBox.setFocus()
            hbox.addWidget(self.searchBox)
            vbox.addLayout(hbox)

        # Create the list widget
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        self.listWidget.currentItemChanged.connect(self.set_value)
        if multiple_selection:
            self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        vbox.addWidget(self.listWidget)

        # Create the button widget
        self.button = QtWidgets.QPushButton("choose")
        self.button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.button.clicked.connect(self.select)
        self.button.setEnabled(False)
        vbox.addWidget(self.button)

        # Set layout
        self.setLayout(vbox)

    def textEdited(self, newText):
        #newText = self.searchBox.text()
        print "Text changed: {0}".format(newText)
        self.shownItems = []
        for item in self.allItems:
            if newText in item:
                self.shownItems.append(item)
        self.setList(self.shownItems)

    def setList(self, l):
        if len(self.allItems) == 0:
            self.allItems = l
            self.shownItems = self.allItems
        self.listWidget.clear()
        for item in l:
            self.listWidget.addItem(item)

#    @Slot(bool)
    def set_value(self, checked):
        if self.multiple_selection:
            if len(self.listWidget.selectedItems()) == 0:
                self.values = [self.listWidget.currentItem().text()]
            else:
                self.values = [x.text() for x in self.listWidget.selectedItems()]
        else:
            self.value = self.listWidget.currentItem().text()
        if self.value != "" or len(self.values) > 0:
            self.button.setEnabled(True)

#    @Slot()
    def select(self):
        if self.multiple_selection:
            self.animated_props = self.values
            self.selected_list.emit(self.values)
        else:
            self.animated_prop = self.value
            self.selected.emit(self.value)
        self.close()
