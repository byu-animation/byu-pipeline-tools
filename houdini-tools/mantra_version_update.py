import os

def update_version(shot, version) :
	directory_list = list()
	print shot
	print version
	path = "/groups/dusk/production/shots/" + str(shot) + "/render"
	print path
#	path = "/groups/dusk/production/shots/a01/render"
	dirs = os.listdir( path )
	dirs.sort()
	highest_version_number = 0
	print "hello world"
	for file in dirs:
		print file
		temp_version = str(highest_version_number)
		if temp_version is file:
			highest_version_number += 1
		else:
			break
	    
#	node = hou.node('/obj/geo1/null1')
	version = highest_version_number
#	return highest_version_number
