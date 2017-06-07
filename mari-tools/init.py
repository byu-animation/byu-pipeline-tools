import os
import mari
import PySide
import sys

def init():
    toolbar = mari.app.findToolBar("BYU Tools")
    if toolbar is not None:
        label = PySide.QtGui.QLabel("BYU Tools")
        toolbar.addWidget(label)

init()

sys.path.append('/users/animation/bdemann/Documents/grendel-dev/byu-pipeline-tools/mari-tools/scripts/')
