try:
    from PySide import QtGui as QtWidgets
    from PySide import QtGui as QtGui
    from PySide import QtCore
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore



class ItemList(QtWidgets.QListWidget):
    all_items = []
    shown_items = []

    def __init__(self, l=[], multiple_selection=False):
        QtWidgets.QListWidget.__init__(self)

        # Create the list widget
        self.shown_items = l
        self.all_items = l
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        if multiple_selection:
            self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

    def set_list(self, l):
        self.clear()
        for item in l:
            self.addItem(item)

class SelectFromList(QtWidgets.QWidget):
    submitted = QtCore.Signal(list)
    values = []

    def __init__(self, parent=None, title="Select", l=[], multiple_selection=False):
        QtWidgets.QWidget.__init__(self)
        if parent:
            self.parent = parent
        self.setWindowTitle(title)
        self.setObjectName('SelectFromList')
        self.multiple_selection = multiple_selection
        self.resize(600,600)
        self.initializeVBox()
        self.setLayout(self.vbox)
        self.show()

    def initializeVBox(self):
        self.vbox = QtWidgets.QVBoxLayout()
        self.initializeSearchBar()
        self.initializeListWidget()
        self.initializeSubmitButton()

    def initializeSearchBar(self):
        # If it's single selection, bring in the searchbox
        if self.multiple_selection:
            return
        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Refine Search: ")
        hbox.addWidget(label)
        self.searchBox = QtWidgets.QLineEdit()
        self.searchBox.textEdited.connect(self.textEdited)
        self.searchBox.setStyleSheet("color: white")
        self.searchBox.setFocus()
        hbox.addWidget(self.searchBox)
        self.vbox.addLayout(hbox)

    def initializeListWidget(self):
        self.listWidget = ItemList(list, self.multiple_selection)
        self.listWidget.itemSelectionChanged.connect(self.select)
        self.vbox.addWidget(self.listWidget)

    def initializeSubmitButton(self):
        # Create the button widget
        self.button = QtWidgets.QPushButton("choose")
        self.button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.button.clicked.connect(self.submit)
        self.button.setEnabled(False)
        self.vbox.addWidget(self.button)

    def set_values(self, values):
        self.values = values
        self.button.setEnabled(len(self.values) > 0)

    def select(self):
        print "selected items: {0}".format(self.listWidget.selectedItems())
        if len(self.listWidget.selectedItems()) == 0:
            self.set_values([])
        else:
            self.set_values([x.text() for x in self.listWidget.selectedItems()])

    def textEdited(self, newText):
        self.listWidget.shown_items = []
        for item in self.listWidget.all_items:
            if newText in item:
                self.listWidget.shown_items.append(item)
        self.listWidget.set_list(self.listWidget.shown_items)
        self.set_values([x.text() for x in self.listWidget.selectedItems()])

    def submit(self):
        self.submitted.emit(self.values)
        self.close()

class SelectFromMultipleLists(SelectFromList):

    labels = []
    lists = []
    currLabel = ""

    submitted = QtCore.Signal(object)

    def __init__(self, parent=None, title="Select from Multiple", lists=[], multiple_selection=False):
        #SelectFromList.__init__(self, parent=parent, title=title, multiple_selection=multiple_selection)
        QtWidgets.QWidget.__init__(self)
        self.setObjectName('SelectFromMultipleLists')
        self.resize(600,600)
        self.setWindowTitle(title)
        self.lists = lists
        self.multiple_selection = multiple_selection

        self.labels = sorted([x for x in lists])
        self.initializeVBox()
        self.setLayout(self.vbox)
        self.currLabel = self.labels[0]
        self.switchList(0, init=True)
        self.show()

    def initializeVBox(self):
        self.vbox = QtWidgets.QVBoxLayout()
        self.initializeDropdown()
        self.initializeSearchBar()
        self.initializeListWidget()
        self.initializeSubmitButton()

    def initializeDropdown(self):
        self.comboBox = QtWidgets.QComboBox()
        for label in self.labels:#[::-1]:
            print "adding label {0}".format(label)
            self.comboBox.addItem(label)
        self.comboBox.currentIndexChanged.connect(self.switchList)
        self.vbox.addWidget(self.comboBox)

    def indexFromLabel(self, label):
        for i, l in enumerate(self.labels):
            if l==label:
                return i

    def switchList(self, index, init=False):
        newLabel = self.labels[index]
        if not init and self.lists[self.currLabel] == self.lists[newLabel]:
            return
        newList = self.lists[newLabel]
        self.currLabel = newLabel
        self.listWidget.all_items = newList
        self.listWidget.shown_items = newList
        print "newList: {0}".format(newList)
        self.listWidget.set_list(newList)
        if not init and self.multiple_selection:
            self.textEdited(self.searchBox.text())
        self.set_values([value for value in self.values if value in self.listWidget.shown_items])

    def submit(self):
        self.submitted.emit((self.currLabel, self.values))
        self.close()
