try:
	from byuam import Environment
	import assemble_v2
	import hou
except Exception as e:
	print(e)
	
print Environment().get_project_dir()
print Environment().get_hda_dir()

#print "attempting to rebuild all assets."

#assemble_v2.rebuildAllAssets()
