# Author: Ben DeMann
import hou
import os
from PySide2 import QtGui, QtWidgets, QtCore
from byugui.inspire_quote_gui import QuoteWindow

def go():
    print "We are about to start the inspire_quote script"
    global quote_window
    quote_window = QuoteWindow(hou.ui.mainQtWindow())
