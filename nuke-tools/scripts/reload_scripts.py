import checkout
import inspire
import nukeAutoComp
import publish
import reload_scripts
import rollback
import comp_template

def go():
	reload(checkout)
	reload(inspire)
	reload(nukeAutoComp)
	reload(publish)
	reload(reload_scripts)
	reload(rollback)
	reload(comp_template)
