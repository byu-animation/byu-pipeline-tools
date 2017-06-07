try:
	from PySide import QtGui as QtWidgets
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtCore

import re

from byuam import Project

def check_user_email(parent=None):
    """
    Check if the current user has an email address. If not, open an email request dialog.
    parent -- the widget to parent the dialog to
    """
    project = Project()
    user = project.get_user()
    if user.get_email()=="":
        dialog = RequestEmailDialog(parent)
        dialog.show()

class RequestEmailDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle("Email")
        # palette = parent.palette
        self.setPalette(parent.palette)

        self.project = Project()
        self.username = self.project.get_current_username()
        self.user = self.project.get_user(self.username)
        self.user_fullname = self.user.get_fullname()

        request_str = '<span style=" font-size:12pt; font-weight:600;">Please input your email address</span>'
        info_str = "username: "+self.username+"\nfull name: "+self.user_fullname
        self.request_label = QtWidgets.QLabel(request_str)
        self.info_label = QtWidgets.QLabel(info_str)

        input_str = "email:"
        self.input_label = QtWidgets.QLabel(input_str)

        self.input = QtWidgets.QLineEdit()
        self.input.textChanged.connect(self._check_valid)

        self.accept_button = QtWidgets.QPushButton("OK")
        self.accept_button.setEnabled(False)
        self.accept_button.clicked.connect(self._store_email)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.request_label)
        self.layout.addWidget(self.info_label)
        self.input_layout = QtWidgets.QHBoxLayout()
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input)
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.accept_button)

    def _check_valid(self, text):
        if re.match(r"[^@]+@[^@]+\.[^@]+", text): # check for valid email address
            self.accept_button.setEnabled(True)
        else:
            self.accept_button.setEnabled(False)

    def _store_email(self):
        self.user.update_email(str(self.input.text()))
        self.done(0)

if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = RequestEmailDialog()
    window.show()
    sys.exit(app.exec_())
