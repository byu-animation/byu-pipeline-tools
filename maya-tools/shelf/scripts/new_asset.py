from PyQt4 import QtGui, QtCore
from byuam.project import Project
from byugui.new_asset_gui import CreateWindow, NewAssetWindow

def go():
    print 'IN GO'
    app = QtGui.QApplication(sys.argv)
    win = CreateWindow()
    print 'CREATED WINDOW'

if __name__ == '__main__':
    print 'IN MAIN'
    go()
