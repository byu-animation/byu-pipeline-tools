import hou
import json
import os

incorrect_job_path = os.environ['JOB']

def go():
	mylist = hou.fileReferences()

	data = json.loads( """{
	    "Remote": {
	        "HOME": "gm_root_users",
	        "JOB": "gm_root"
	    },
	    "File": {

	   }
	}""")

	for parm, path in mylist:
	    data["File"][hou.expandString(path)]=True

	manifestFile = "{0}/.gridmarkets/manifest".format(os.path.dirname(hou.hipFile.path()))
	if not os.path.exists(os.path.dirname(manifestFile)):
		os.makedirs(os.path.dirname(manifestFile))

	with open(manifestFile, 'w+') as outfile:
	    json.dump(data,outfile)
