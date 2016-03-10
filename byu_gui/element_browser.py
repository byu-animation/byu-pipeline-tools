from PyQt4 import QtGui, QtCore

import os

from byuam.body import Asset, Shot
from byuam.environment import AssetType, Department, Status
from byuam.project import Project

REF_WINDOW_WIDTH = 800
REF_WINDOW_HEIGHT = 500

class TreeComboBoxItem(QtGui.QComboBox):
    def __init__(self, tree_item, column):
        QtGui.QComboBox.__init__(self)
        self.tree_item = tree_item
        self.column = column
        self.currentIndexChanged.connect(self._change_item)
        
    def _change_item(self, index):
        self.tree_item.setText(self.column, self.itemText(index))

class ElementBrowser(QtGui.QWidget):

    ASSETS = "Asset"
    SHOTS = "Shots"

    BODY_DATA_COLUMN = 1

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setGeometry(0, 0, REF_WINDOW_WIDTH, REF_WINDOW_HEIGHT)

        # initialize project info
        self.project = Project()
        self.assets = self.project.list_assets()
        self.shots = self.project.list_shots()
        self.bodies = self.assets

        # status bar
        self.status_bar = QtGui.QStatusBar()

        # asset/shot menu
        self.body_menu = QtGui.QComboBox()
        self.body_menu.addItem(self.ASSETS)
        self.body_menu.addItem(self.SHOTS)
        self.current_body = self.ASSETS
        self._set_bodies()

        # tree
        self.tree = QtGui.QTreeWidget()
        self.columnCount = 7
        self.tree.setColumnCount(self.columnCount)
        tree_header = QtGui.QTreeWidgetItem(["name", "", "assigned", "status", "start", "end", "publish"])
        self.tree.setHeaderItem(tree_header)

        self.init_tree = [None]*self.columnCount
        self.init_tree[0] = self.init_name
        self.init_tree[1] = self.init_dept
        self.init_tree[2] = self.init_assigned_user
        self.init_tree[3] = self.init_status
        self.init_tree[4] = self.init_start_date
        self.init_tree[5] = self.init_end_date
        self.init_tree[6] = self.init_last_publish

        self._build_tree()

        self.update_tree = [None]*self.columnCount
        self.update_tree[0] = self.update_name
        self.update_tree[1] = self.update_dept
        self.update_tree[2] = self.update_assigned_user
        self.update_tree[3] = self.update_status
        self.update_tree[4] = self.update_start_date
        self.update_tree[5] = self.update_end_date
        self.update_tree[6] = self.update_last_publish

        # connect events
        self.body_menu.currentIndexChanged.connect(self._body_changed)
        self.tree.itemExpanded.connect(self._load_elements)
        self.tree.itemChanged.connect(self._item_edited)

        # layout
        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setMargin(6)
        layout.addWidget(self.body_menu)
        layout.addWidget(self.tree)
        layout.addWidget(self.status_bar)
        self.setLayout(layout)

    def _build_tree(self):
        self.tree.clear()
        tree_state = self.tree.blockSignals(True)
        for body in self.bodies:
            tree_item = QtGui.QTreeWidgetItem([body])
            self.tree.addTopLevelItem(tree_item)
            tree_flags = tree_item.flags()
            tree_item.setFlags(tree_flags | QtCore.Qt.ItemIsEditable)
            body_obj = self.project.get_body(body)
            self._load_body(body_obj, tree_item)
            tree_item.addChild(QtGui.QTreeWidgetItem()) # empty item

            # tree_item.emitDataChanged.connect(self._item_edited)
            # body_obj = self.project.get_body(body)
            # elements = []
            # for dept in Department.ALL:
            #     elements = elements + body_obj.list_elements(dept)
            # # elements = body_obj.list_elements(self.dept)
            # for element in elements:
            #     element_obj = body_obj.get_element(self.dept, element)
            #     # element_data = self._element_data(element_obj)
            #     child_item = QtGui.QTreeWidgetItem()
            #     tree_item.addChild(child_item)
            #     child_item.setData(0, QtCore.Qt.UserRole, QtCore.QVariant(element))
            #     child_flags = child_item.flags()
            #     child_item.setFlags(child_flags | QtCore.Qt.ItemIsEditable)
            #     for col, init in enumerate(self.init_tree):
            #         init(element_obj, child_item, col)
                # references = body_obj.get_element(self.dept, element).list_cache_files() # TODO: list_references
                # for ref in references:
                #     ref_item = QtGui.QTreeWidgetItem([ref])
                #     ref_item.setData(0, QtCore.Qt.UserRole, QtCore.QVariant(ref))
                #     child_item.addChild(ref_item)

            # body_combobox = TreeComboBoxItem(tree_item, 1)
            # body_type = body_obj.get_type()
            # type_idx = 0
            # for idx, type in enumerate(AssetType.ALL):
            #     body_combobox.addItem(type)
            #     if type == body_type:
            #         type_idx = idx
            # body_combobox.setCurrentIndex(type_idx)
            # self.tree.setItemWidget(tree_item, 1, body_combobox)

        self.tree.blockSignals(tree_state)

    def _load_body(self, body, item):
        tree_state = self.tree.blockSignals(True)
        item.setText(0, body.get_name())
        namelabel = QtGui.QLabel(body.get_name())
        namelabel.setAutoFillBackground(True)
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
            emptylabel = QtGui.QLabel()
            emptylabel.setAutoFillBackground(True)
            self.tree.setItemWidget(item, col, emptylabel)
            

        self.tree.blockSignals(tree_state)

    def _load_elements(self, item):
        tree_state = self.tree.blockSignals(True)
        body = str(item.text(0))
        body_obj = self.project.get_body(body)
        elements = []
        for dept in Department.ALL:
            dept_elements = body_obj.list_elements(dept)
            for dept_element in dept_elements:
                elements.append((dept, dept_element))
        item.takeChildren() # clear children
        for dept, element in elements:
            element_obj = body_obj.get_element(dept, element)
            child_item = QtGui.QTreeWidgetItem()
            item.addChild(child_item)
            child_item.setFlags(child_item.flags() | QtCore.Qt.ItemIsEditable)
            # child_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            for col, init in enumerate(self.init_tree):
                init(element_obj, child_item, col)
        self.tree.blockSignals(tree_state)

    def _set_bodies(self):
        if self.current_body == self.ASSETS:
            self.bodies = self.project.list_assets()
        elif self.current_body == self.SHOTS:
            self.bodies = self.project.list_shots()
        else:
            self.bodies = []

    def _item_edited(self, item, column):

        print item.text(column)
        parent = item.parent()
        if parent is not None:
            body = str(parent.text(0))
            body_obj = self.project.get_body(body)
            element = str(item.text(0))
            dept = str(item.text(1))
            print dept
            element_obj = body_obj.get_element(dept, element)
            self.update_tree[column](element_obj, item, column)
            # self.tree.resizeColumnToContents(column)
        else:
            body = str(item.text(0))
            body_obj = self.project.get_body(body)
            self._update_body_data(body_obj, item)

    def _body_changed(self, index):
        self.current_body = str(self.body_menu.itemText(index))
        self._set_bodies()
        self._build_tree()
        self.status_bar.clearMessage()

    def _update_body_data(self, body, item):
        if self.current_body==self.ASSETS:
            body.update_type(str(item.text(self.BODY_DATA_COLUMN)))
        elif self.current_body==self.SHOTS:
            body.update_frame_range(int(item.text(self.BODY_DATA_COLUMN)))
        else:
            self.status_bar.showMessage("Error: unknown body type")

    def init_name(self, element, item, column):
        item.setText(column, element.get_name())
        namelabel = QtGui.QLabel(element.get_name())
        namelabel.setAutoFillBackground(True)
        self.tree.setItemWidget(item, column, namelabel)

    def init_dept(self, element, item, column):
        item.setText(column, element.get_department())
        deptlabel = QtGui.QLabel(element.get_department())
        deptlabel.setAutoFillBackground(True)
        self.tree.setItemWidget(item, column, deptlabel)

    def init_assigned_user(self, element, item, column):
        item.setText(column, element.get_assigned_user())

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

    def update_name(self, element, item, column):
        self.status_bar.showMessage("can't change name")

    def update_dept(self, element, item, column):
        self.status_bar.showMessage("can't change department")

    def update_assigned_user(self, element, item, column):
        element.update_assigned_user(str(item.text(column)))
        self.status_bar.clearMessage()

    def update_status(self, element, item, column):
        element.update_status(str(item.text(column)))
        self.status_bar.clearMessage()

    def update_start_date(self, element, item, column):
        self.status_bar.showMessage("update start date not implemented")

    def update_end_date(self, element, item, column):
        self.status_bar.showMessage("update end date not implemented")

    def update_last_publish(self, element, item, column):
        self.status_bar.showMessage("can't modify publish data")
        self.init_last_publish(element, item, column)

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = ElementBrowser()
    window.show()
    sys.exit(app.exec_())
