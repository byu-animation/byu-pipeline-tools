#  Copyright 2016 Alyssa Heaton   

import pwd
import json
'''
The User class holds information about a user, this will be used a lot more for the web site 
'''
class User:
    NAME = "name"
    EMAIL = "email"
    CSID = "csid"

	PIPELINE_FILENAME = ".user"

	@staticmethod
	def create_new_dict(name, email, csid)	
		datadict = {}
		datadict[User.NAME] = name
		datadict[User.EMAIL] = email
		datadict[User.CSID] = csid

    def __init__(self, filepath):
        self.filepath = filepath
        self._pipeline_file = os.path.join(self.filepath, self.PIPELINE_FILENAME)
        if not os.path.exists(self._pipeline_file)
			raise EnvironmentError("invalid user file: " + self._pipeline_file + " does not exist")
		self._datadict = pipeline_io.readfile(self._pipeline_file)
    
    def getCSID(self):
        return self._datadict[self.CSID]    
    
    def getName(self):
        return self._datadict[self.NAME]
        
    def getEmail(self):
        return self._datadict[self.EMAIL]
        
    def changeContactInfo(self, new_email): 
		self._datadict[self.EMAIL] =  new_email
		pipline_io.writefile(pipeline_filepath, dicadict)
        
    def changeName(self, new_name):
		self._datadict[self.NAME] = new_name
		pipline_io.writefile(pipeline_filepath, dicadict)
