from byugui.new_asset_gui import CreateWindow, NewAssetWindow
from PySide2 import QtWidgets
import hou
import os

def go():
    global quote_window
    dialog = CreateWindow(hou.ui.mainQtWindow())
