try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore


class SelectFromMultipleLists(SelectFromList):

	labels = []
	lists = []
	currLabel = ""

	submitted = QtCore.Signal(object)
	def __init__(self, lists, parent=None, multiple_selection=False):
		self.setObjectName('SelectFromMultipleLists')
        self.resize(600,600)
		self.labels = [x for x in lists].sort()
        self.initializeVBox()
		self.setLayout(self.vbox)

		self.lists = lists
		self.currLabel = labels[0]
		self.switchList(self.currLabel)

	self.initializeVBox(self):
		self.vbox = QtWidgets.QVBoxLayout()
		self.initializeDropdown()
		self.initializeSearchBar()
		self.initializeListWidget()
		self.initializeSubmitButton()

	def initializeDropdown(self):
		comboBox = QtWidgets.QComboBox()
		for label in self.labels[::-1]:
			comboBox.insertItem(0, label)
		comboBox.currentIndexChanged.connect(self.switchList)
		self.vbox.addLayout(comboBox)

	def switchList(self, i):
		newLabel = labels[i]
		if index > len(lists) or lists[currLabel] == lists[newLabel]:
			return
		newList = lists[newLabel]
		self.currLabel = newLabel
		self.listWidget.all_items = self.listWidget.shown_items = newList
		self.listWidget.set_list(newList)
		if self.multiple_selection:
			self.textEdited(self.searchBox.text())
		self.values = [value for value in self.values if value in self.listWidget.shown_items]

class SelectFromList(QtWidgets.QWidget):
    submitted = QtCore.Signal(list)
    values = []

	def __init__(self, parent=None, list=[], multiple_selection=False):
		super(SelectFromSingleList, self).__init__()
        self.setObjectName('SelectFromList')

		self.multiple_selection = multiple_selection
        self.resize(600,600)
		self.initializeVBox()
        self.setLayout(self.vbox)

	def initializeVBox(self):
		self.vbox = QtWidgets.QVBoxLayout()
		self.initializeSearchBar()
		self.initializeListWidget()
		self.initializeSubmitButton()

	def initializeSearchBar(self, vbox):
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
		self.listWidget = ItemList(list, multiple_selection)
		self.listWidget.currentItemChanged.connect(self.select)
		self.vbox.addWidget(listWidget)

	def initializeSubmitButton(self):
		# Create the button widget
        self.button = QtWidgets.QPushButton("choose")
        self.button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.button.clicked.connect(self.submit)
        self.button.setEnabled(False)
        self.vbox.addWidget(self.button)

    def select(self, checked):
        if len(self.item_list.listWidget.selectedItems()) == 0:
            self.values = []
        else:
            self.values = [x.text() for x in self.item_list.listWidget.selectedItems()]
        if len(self.values) > 0:
            self.button.setEnabled(True)

    def textEdited(self, newText):
        self.listWidget.shown_items = []
        for item in self.listWidget.all_items:
            if newText in item:
                self.listWidget.shown_items.append(item)
        self.set_list(self.listWidget.shown_items)

    def submit(self):
        self.submitted.emit(self.values)
        self.close()

class ItemList(QtWidgets.QListWidget):
    all_items = []
    shown_items = []

    def __init__(self, list=[], multiple_selection=False):
        super(SelectFromList, self).__init__()

        # Create the list widget
		self.shown_items = self.all_items = l
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        if multiple_selection:
            self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

    def set_list(self, l):
        self.clear()
        for item in l:
            self.addItem(item)
