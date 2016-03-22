from byugui.checkout_gui import CheckoutWindow
from PyQt4 import QtCore
import maya.OpenMayaUI as omu
import sip

def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)
    
def go():
    parent = maya_main_window()
    dialog = CheckoutWindow(parent)
