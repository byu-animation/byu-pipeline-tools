import os
import mari
import PySide

def init():
    toolbar = mari.app.findToolBar("BYU Tools")
    if toolbar is not None:
        label = PySide.QtGui.QLabel("BYU Tools")
        toolbar.addWidget(label)

init()
