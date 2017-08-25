import assemble_texture
import checkout
import inspire
import publish
import reload_scripts
import rollback

def go():
	reload(assemble_texture)
	reload(checkout)
	reload(inspire)
	reload(publish)
	reload(reload_scripts)
	reload(rollback)
