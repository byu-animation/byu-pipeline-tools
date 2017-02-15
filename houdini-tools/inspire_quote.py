# Author: Ben DeMann
import hou
import os
from PyQt4 import QtGui, QtCore
from byugui.inspire_quote_gui import QuoteWindow
        
def go():
    global quote_window
    quote_window = QuoteWindow(hou.ui.mainQtWindow())
