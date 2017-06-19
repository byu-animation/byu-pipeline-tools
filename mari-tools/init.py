import os
import mari
import PySide
import sys
from byuam import Project

def init():
    toolbar = mari.app.findToolBar("BYU Tools")
    if toolbar is not None:
        label = PySide.QtGui.QLabel("BYU Tools")
        toolbar.addWidget(label)

init()

project = Project()

script_path = os.path.join(project.get_project_dir(), 'byu-pipeline-tools/mari-tools/scripts/')

sys.path.append(script_path)
