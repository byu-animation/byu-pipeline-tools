import mari
import inspire
import checkout
import publish
import assemble_texture
import export_images

inpire_button = mari.actions.create('Inspirational Quote', 'inspire.go()')
checkout_button = mari.actions.create('Checkout', 'checkout.go()')
export_all_button = mari.actions.create('Export All Tex', 'export_images.go(export_images.ALL)')
export_geo_button = mari.actions.create('Export Selected Geo Tex', 'export_images.go(export_images.SELECTED_GEO)')
export_channel_button = mari.actions.create('Export Selected Channel Tex', 'export_images.go(export_images.SELECTED_CHANNEL)')
assemble_button = mari.actions.create('Assemble Texuture', 'assemble_texture.go()')
publish_button = mari.actions.create('Publish', 'publish.go()')

mari.menus.addAction(export_all_button, "MainWindow/&BYU Tools/Tex Export")
mari.menus.addAction(export_geo_button, "MainWindow/&BYU Tools/Tex Export")
mari.menus.addAction(export_channel_button, "MainWindow/&BYU Tools/Tex Export")
mari.menus.addAction(assemble_button, "MainWindow/&BYU Tools")
mari.menus.addAction(checkout_button, "MainWindow/&BYU Tools")
mari.menus.addAction(publish_button, "MainWindow/&BYU Tools")
mari.menus.addAction(inpire_button, "MainWindow/&BYU Tools")
