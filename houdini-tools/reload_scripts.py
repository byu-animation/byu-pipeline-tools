import assemble_asset
import checkout
import create_tool_hda
import inspire_quote
import new_body
import publish
import renderman_setup
import rollback
import test_geo
import tractor_submit
import reload_scripts
import render_callbacks
import matchDefinition
import assemble_v2
import menu_scripts
import byuam
import import_shot

def go():
	reload(assemble_asset)
	reload(checkout)
	reload(create_tool_hda)
	reload(inspire_quote)
	reload(new_body)
	reload(publish)
	reload(reload_scripts)
	reload(render_callbacks)
	reload(renderman_setup)
	reload(rollback)
	reload(test_geo)
	reload(tractor_submit)
	reload(matchDefinition)
	reload(import_shot)
	reload(byuam)
	reload(assemble_v2)
	reload(menu_scripts)

	print ('Scripts reloaded')
