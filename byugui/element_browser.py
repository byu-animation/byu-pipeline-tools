from PyQt4 import QtGui, QtCore

import datetime
import operator
import os

from byuam.body import Asset, Shot
from byuam.environment import AssetType, Department, Status
from byuam.project import Project

from byugui import request_email

REF_WINDOW_WIDTH = 1000
REF_WINDOW_HEIGHT = 625

class TreeComboBoxItem(QtGui.QComboBox):

    def __init__(self, tree_item, column):
        QtGui.QComboBox.__init__(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.tree_item = tree_item
        self.column = column
        self.currentIndexChanged.connect(self._change_item)
        
    def _change_item(self, index):
        self.tree_item.setText(self.column, self.itemText(index))

    def wheelEvent(self, e):
        e.ignore() # do nothing

    def paintEvent(self, pe):
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(1)
        pen.setColor
        painter.setPen(pen)
        painter.drawRect(pe.rect())
        painter.end()
        
        QtGui.QComboBox.paintEvent(self, pe)

class TreeLineEdit(QtGui.QLineEdit):

    def __init__(self, contents, tree_item, column):
        QtGui.QLineEdit.__init__(self, contents)
        self.tree_item = tree_item
        self.column = column
        self.editingFinished.connect(self._change_item)

    def _change_item(self):
        self.tree_item.setText(self.column, self.text())

    def paintEvent(self, pe):
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(1)
        pen.setColor
        painter.setPen(pen)
        painter.drawRect(pe.rect())
        painter.end()
        
        QtGui.QLineEdit.paintEvent(self, pe)

class TreeLabel(QtGui.QLabel):

    def __init__(self, text=""):
        QtGui.QLabel.__init__(self, text)
        self.setAutoFillBackground(True)
    
    def paintEvent(self, pe):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(self.palette().color(QtGui.QPalette.AlternateBase))
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(1)
        pen.setColor
        painter.setPen(pen)
        painter.drawRect(pe.rect())
        painter.end()
        
        QtGui.QLabel.paintEvent(self, pe)

class TreeGridDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        painter.save()
        # painter.setPen(option.palette.color(QtGui.QPalette.Text))
        painter.setPen(QtCore.Qt.black)
        painter.drawRect(option.rect)
        painter.restore()

        QtGui.QStyledItemDelegate.paint(self, painter, option, index)

class ElementBrowser(QtGui.QWidget):

    ASSETS = "Assets"
    SHOTS = "Shots"

    BODY_DATA_COLUMN = 1

    @staticmethod
    def dark_palette():
        palette = QtGui.QPalette()
        base_color = QtGui.QColor(39,39,39)
        alt_color = QtGui.QColor(30,30,30)
        text_color = QtGui.QColor(192,192,192)
        highlight_color = QtGui.QColor(57,86,115)
        highlight_text_color = QtCore.Qt.white
        disabled_alt_color = QtGui.QColor(49,49,49)
        disabled_base_color = QtGui.QColor(40,40,40)
        disabled_text_color = QtGui.QColor(100,100,100)
        palette.setColor(QtGui.QPalette.Window, base_color)
        palette.setColor(QtGui.QPalette.WindowText, text_color)
        palette.setColor(QtGui.QPalette.Base, base_color)
        palette.setColor(QtGui.QPalette.AlternateBase, alt_color)
        palette.setColor(QtGui.QPalette.ToolTipBase, alt_color)
        palette.setColor(QtGui.QPalette.ToolTipText, text_color)
        palette.setColor(QtGui.QPalette.Button, base_color)
        palette.setColor(QtGui.QPalette.ButtonText, text_color)
        palette.setColor(QtGui.QPalette.Text, text_color)
        palette.setColor(QtGui.QPalette.Highlight, highlight_color)
        palette.setColor(QtGui.QPalette.HighlightedText, highlight_text_color)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Window, disabled_base_color)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, disabled_text_color)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base, disabled_text_color)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, disabled_alt_color)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button, disabled_base_color)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabled_text_color)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabled_text_color)
        return palette

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle("Element Browser")
        self.setGeometry(0, 0, REF_WINDOW_WIDTH, REF_WINDOW_HEIGHT)
        self.palette = self.dark_palette()
        self.setPalette(self.palette)

        # initialize project
        self.project = Project()
        self.userList = self.project.list_users()

        #filters
        self.filter_label = QtGui.QLabel("Filter by: ")

        self.dept_filter_label = QtGui.QLabel("Department")
        self.dept_filter_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.dept_filter = QtGui.QComboBox()
        self.dept_filter.addItem("all")
        for each in Department.ALL:
            self.dept_filter.addItem(each)
        self.dept_list = Department.ALL

        self.type_filter_label = QtGui.QLabel("Asset Type")
        self.type_filter_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.type_filter = QtGui.QComboBox()
        self.type_filter.addItem("all")
        for each in AssetType.ALL:
            self.type_filter.addItem(each)

        # menu bar
        self.menu_bar = QtGui.QMenuBar()
        self.view_menu = QtGui.QMenu("View")
        self.menu_bar.addMenu(self.view_menu)
        self.expand_action = self.view_menu.addAction("Expand All")

        # asset/shot menu
        self.body_menu = QtGui.QComboBox()
        self.body_menu.addItem(self.ASSETS)
        self.body_menu.addItem(self.SHOTS)
        self.current_body = self.ASSETS
        self._set_bodies()

        # new button
        self.new_button = QtGui.QPushButton("New")

        # refresh button
        self.refresh_button = QtGui.QPushButton("Refresh")

        # tree
        self.tree = QtGui.QTreeWidget()
        self.tree.setItemDelegate(TreeGridDelegate(self.tree))
        self.columnCount = 8
        self.tree.setColumnCount(self.columnCount)
        tree_header = QtGui.QTreeWidgetItem(["name", "", "assigned", "status", "start", "end", "publish", "note"])
        self.tree.setHeaderItem(tree_header)

        self.init_tree = [None]*self.columnCount
        self.init_tree[0] = self.init_name
        self.init_tree[1] = self.init_dept
        self.init_tree[2] = self.init_assigned_user
        self.init_tree[3] = self.init_status
        self.init_tree[4] = self.init_start_date
        self.init_tree[5] = self.init_end_date
        self.init_tree[6] = self.init_last_publish
        self.init_tree[7] = self.init_note

        self._build_tree()

        self.update_tree = [None]*self.columnCount
        self.update_tree[0] = self.update_name
        self.update_tree[1] = self.update_dept
        self.update_tree[2] = self.update_assigned_user
        self.update_tree[3] = self.update_status
        self.update_tree[4] = self.update_start_date
        self.update_tree[5] = self.update_end_date
        self.update_tree[6] = self.update_last_publish
        self.update_tree[7] = self.update_note
        
        # status bar
        self.status_bar = QtGui.QStatusBar()

        # connect events
        self.expand_action.triggered.connect(self._expand_all)
        self.body_menu.currentIndexChanged.connect(self._body_changed)
        self.new_button.clicked.connect(self._new_body)
        self.refresh_button.clicked.connect(self._refresh)
        self.tree.itemExpanded.connect(self._load_elements)
        self.tree.itemChanged.connect(self._item_edited)
        self.dept_filter.currentIndexChanged.connect(self._dept_filter_changed)
        self.type_filter.currentIndexChanged.connect(self._refresh)

        # layout
        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setMargin(6)
        options_layout = QtGui.QGridLayout()
        options_layout.addWidget(self.body_menu, 0, 0)
        options_layout.addWidget(self.new_button, 0, 1)
        options_layout.addWidget(self.refresh_button, 0, 3)
        options_layout.setColumnMinimumWidth(0, 100)
        options_layout.setColumnMinimumWidth(1, 100)
        options_layout.setColumnMinimumWidth(3, 100)
        options_layout.setColumnStretch(2, 1)
        filter_layout = QtGui.QGridLayout()
        filter_layout.addWidget(self.filter_label, 0, 0)
        filter_layout.addWidget(self.dept_filter_label, 0, 1)
        filter_layout.addWidget(self.dept_filter, 0, 2)
        filter_layout.addWidget(self.type_filter_label, 0, 3)
        filter_layout.addWidget(self.type_filter, 0, 4)
        filter_layout.setColumnMinimumWidth(0, 50)
        filter_layout.setColumnMinimumWidth(1, 100)
        filter_layout.setColumnMinimumWidth(2, 100)
        filter_layout.setColumnMinimumWidth(3, 100)
        filter_layout.setColumnMinimumWidth(4, 100)
        filter_layout.setColumnStretch(5, 1)
        layout.addWidget(self.menu_bar)
        layout.addLayout(options_layout)
        layout.addWidget(self.tree)
        layout.addLayout(filter_layout)
        # layout.addWidget(self.filter_label)
        # layout.addWidget(self.type_filter)
        # layout.addWidget(self.dept_filter)
        layout.addWidget(self.status_bar)
        self.setLayout(layout)

        request_email.check_user_email(self)

    def _build_tree(self):
        self.tree.clear()
        tree_state = self.tree.blockSignals(True)
        for body in self.bodies:
            tree_item = QtGui.QTreeWidgetItem([body])
            self.tree.addTopLevelItem(tree_item)
            tree_flags = tree_item.flags()
            tree_item.setFlags(tree_flags | QtCore.Qt.ItemIsEditable)
            # for col in xrange(self.columnCount):
            #     tree_item.setBackground(col, QtGui.QColor(30,30,30))
            body_obj = self.project.get_body(body)
            self._load_body(body_obj, tree_item)
            tree_item.addChild(QtGui.QTreeWidgetItem()) # empty item
        self.tree.blockSignals(tree_state)

    def _load_body(self, body, item):
        tree_state = self.tree.blockSignals(True)
        item.setText(0, body.get_name())
        namelabel = TreeLabel(body.get_name())
        self.tree.setItemWidget(item, 0, namelabel)
        if self.current_body==self.ASSETS:
            body_type = body.get_type()
            item.setText(self.BODY_DATA_COLUMN, body_type)
            combobox = TreeComboBoxItem(item, self.BODY_DATA_COLUMN)
            type_idx = 0
            for idx, type in enumerate(AssetType.ALL):
                combobox.addItem(type)
                if type == body_type:
                    type_idx = idx
            combobox.setCurrentIndex(type_idx)
            self.tree.setItemWidget(item, self.BODY_DATA_COLUMN, combobox)
        elif self.current_body==self.SHOTS:
            item.setText(1, str(body.get_frame_range()))
        else:
            self.status_bar.showMessage("Error: unknown body type")
        for col in xrange(self.BODY_DATA_COLUMN+1, self.columnCount): # disable remaining columns
            emptylabel = TreeLabel()
            self.tree.setItemWidget(item, col, emptylabel)
        self.tree.blockSignals(tree_state)

    def _load_elements(self, item):
        tree_state = self.tree.blockSignals(True)
        body = str(item.text(0))
        body_obj = self.project.get_body(body)
        elements = []
        for dept in self.dept_list:
            dept_elements = body_obj.list_elements(dept)
            for dept_element in dept_elements:
                elements.append((dept, dept_element))
        item.takeChildren() # clear children
        for dept, element in elements:
            element_obj = body_obj.get_element(dept, element)
            child_item = QtGui.QTreeWidgetItem()
            item.addChild(child_item)
            child_item.setFlags(child_item.flags() | QtCore.Qt.ItemIsEditable)
            for col, init in enumerate(self.init_tree):
                init(element_obj, child_item, col)
        self.tree.blockSignals(tree_state)

    def _expand_all(self):
        # self.tree.expandAll()
        count = self.tree.topLevelItemCount()
        for i in xrange(count):
            item = self.tree.topLevelItem(i)
            self.tree.expandItem(item)
            

    def _set_bodies(self):
        if self.current_body == self.ASSETS:
            asset_filter = None
            if(self.type_filter.currentIndex()):
                asset_filter_str = str(self.type_filter.currentText())
                asset_filter = (Asset.TYPE, operator.eq, asset_filter_str)
            self.bodies = self.project.list_assets(asset_filter)
        elif self.current_body == self.SHOTS:
            self.bodies = self.project.list_shots()
        else:
            self.bodies = []

    def _item_edited(self, item, column):
        parent = item.parent()
        if parent is not None:
            body = str(parent.text(0))
            body_obj = self.project.get_body(body)
            element = str(item.text(0))
            dept = str(item.text(1))
            element_obj = body_obj.get_element(dept, element)
            self.update_tree[column](element_obj, item, column)
            # self.tree.resizeColumnToContents(column)
        else:
            body = str(item.text(0))
            body_obj = self.project.get_body(body)
            self._update_body_data(body_obj, item)

    def _refresh(self): # TODO: maintain expanded rows on refresh
        self._set_bodies()
        self._build_tree()
        self.status_bar.clearMessage()

    def _body_changed(self, index):
        self.current_body = str(self.body_menu.itemText(index))
        if(self.body_menu.currentIndex()):
            self.type_filter.setEnabled(False)
            self.type_filter_label.setEnabled(False)
        else:
            self.type_filter.setEnabled(True)
            self.type_filter_label.setEnabled(True)
        self._refresh()

    def _dept_filter_changed(self):
        if(self.dept_filter.currentIndex()):
            self.dept_list = [str(self.dept_filter.currentText())]
        else:
            self.dept_list = Department.ALL
        self._refresh()

    def _new_body(self):
        from byugui import new_asset_gui
        self.new_body_dialog = new_asset_gui.CreateWindow(self)
        if self.current_body == self.ASSETS:
            self.new_body_dialog.setCurrentIndex(self.new_body_dialog.ASSET_INDEX)
        elif self.current_body == self.SHOTS:
            self.new_body_dialog.setCurrentIndex(self.new_body_dialog.SHOT_INDEX)
        self.new_body_dialog.finished.connect(self._refresh)

    def _update_body_data(self, body, item):
        if self.current_body==self.ASSETS:
            body.update_type(str(item.text(self.BODY_DATA_COLUMN)))
        elif self.current_body==self.SHOTS:
            body.update_frame_range(int(item.text(self.BODY_DATA_COLUMN)))
        else:
            self.status_bar.showMessage("Error: unknown body type")

    def _valid_date(self, date):
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            return str(date_obj)
        except ValueError:
            self.status_bar.showMessage(date+" not a valid date, please use format: YYYY-MM-DD")
            return None

    def init_name(self, element, item, column):
        item.setText(column, element.get_name())
        namelabel = TreeLabel(element.get_name())
        self.tree.setItemWidget(item, column, namelabel)

    def init_dept(self, element, item, column):
        item.setText(column, element.get_department())
        deptlabel = TreeLabel(element.get_department())
        self.tree.setItemWidget(item, column, deptlabel)

    def init_assigned_user(self, element, item, column):
        user = element.get_assigned_user()
        item.setText(column, user)
        lineedit = TreeLineEdit(user, item, column)
        userCompleter = QtGui.QCompleter(self.userList)
        lineedit.setCompleter(userCompleter)
        self.tree.setItemWidget(item, column, lineedit)

    def init_status(self, element, item, column):
        item.setText(column, element.get_status())
        combobox = TreeComboBoxItem(item, column)
        element_type = element.get_status()
        type_idx = 0
        for idx, type in enumerate(Status.ALL):
            combobox.addItem(type)
            if type == element_type:
                type_idx = idx
        combobox.setCurrentIndex(type_idx)
        self.tree.setItemWidget(item, column, combobox)

    def init_start_date(self, element, item, column):
        item.setText(column, element.get_start_date())

    def init_end_date(self, element, item, column):
        item.setText(column, element.get_end_date())

    def init_last_publish(self, element, item, column):
        publish = element.get_last_publish()
        if publish is not None:
            item.setText(column, publish[0]+", "+publish[1]+", "+publish[2])
        else:
            item.setText(column, "")

    def init_note(self, element, item, column):
        item.setText(column, element.get_last_note())

    def update_name(self, element, item, column):
        self.status_bar.showMessage("can't change name")

    def update_dept(self, element, item, column):
        self.status_bar.showMessage("can't change department")

    def update_assigned_user(self, element, item, column):
        user = str(item.text(column))
        if user in self.userList:
            element.update_assigned_user(user)
            self.status_bar.clearMessage()
        else:
            self.tree.itemWidget(item, column).setText(element.get_assigned_user())
            self.status_bar.showMessage('"' + user + '" is not a valid username')

    def update_status(self, element, item, column):
        element.update_status(str(item.text(column)))
        self.status_bar.clearMessage()

    def update_start_date(self, element, item, column):
        date_str = str(item.text(column))
        valid_date_str = self._valid_date(date_str)
        if valid_date_str:
            element.update_start_date(valid_date_str)
            self.status_bar.clearMessage()
        else:
            self.init_start_date(element, item, column)

    def update_end_date(self, element, item, column):
        date_str = str(item.text(column))
        valid_date_str = self._valid_date(date_str)
        if valid_date_str:
            element.update_end_date(valid_date_str)
            self.status_bar.clearMessage()
        else:
            self.init_end_date(element, item, column)

    def update_last_publish(self, element, item, column):
        self.status_bar.showMessage("can't modify publish data")
        self.init_last_publish(element, item, column)

    def update_note(self, element, item, column):
        element.update_notes(str(item.text(column)))
        self.status_bar.clearMessage()

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = ElementBrowser()
    window.show()
    sys.exit(app.exec_())
