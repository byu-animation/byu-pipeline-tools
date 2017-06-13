import mari
import inspire
import checkout
import publish
import assemble_texture

inpire_button = mari.actions.create('Inspirational Quote', 'inspire.go()')
checkout_button = mari.actions.create('Checkout', 'checkout.go()')
export_button = mari.actions.create('Export Tex', 'publish.exportTex()')
assemble_button = mari.actions.create('Assemble Texuture', 'assemble_texture.go()')
publish_button = mari.actions.create('Publish', 'publish.go()')

mari.menus.addAction(export_button, "MainWindow/&BYU Tools")
mari.menus.addAction(assemble_button, "MainWindow/&BYU Tools")
mari.menus.addAction(checkout_button, "MainWindow/&BYU Tools")
mari.menus.addAction(publish_button, "MainWindow/&BYU Tools")
mari.menus.addAction(inpire_button, "MainWindow/&BYU Tools")
