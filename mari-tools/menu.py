import mari
import inspire

action = mari.actions.create('Inspirational Quote', 'inspire.go()')
mari.menus.addAction(action, "MainWindow/BYU Tools")
