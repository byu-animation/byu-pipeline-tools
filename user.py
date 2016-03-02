#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  user.py
#  
#  Copyright 2016 Alyssa Heaton 
#  

import pwd

class User:
    NAME = "importantPerson"
    EMAIL = "@faker.com"
    CSID = "NoIdea"
    
    def __init__(self, newCSId, newName, newEmail):
        self.NAME = newName
        self.EMAIL = newEmail
        self.CSID = newCSId
    
    def getCSID(self):
        return self.CSID    
    
    def getName(self):
        return self.NAME
        
    def getEmail(self):
        return self.EMAIL
        
    def changeContactInfo(self, newEmail): 
        self.EMAIL = newEmail
        
    def changeName(self, newName):
		self.NAME = newName

    def changeStudentInfo(self, newUserID): 
        self.userID = newUserID

class UserManager:    
    
    USERLIST = []
    
    def __init__(self):
        self.USERLIST = []
        
        
    def getUser(self, CSID):
		
		if len(self.USERLIST) == 0:
			return "Empty list"
		
		for i in range(len(self.USERLIST)):
			if self.USERLIST[i].getCSID() == CSID:
				return self.USERLIST[i]
			
		return "No such User"       
       
        
    def createUser(self, newCSID):     
        
        tester = self.getUser(newCSID)
        if tester == "No such User" or tester == "Empty list":
			#print "user already exists"
		 
			CSID = newCSID
			userInfo = pwd.getpwnam(newCSID)
			FULLNAME = userInfo.pw_gecos
			NAME = FULLNAME
			EMAIL = "DEFALT"
			self.USERLIST.append(User(CSID, NAME, EMAIL))
 
   
if __name__== "__main__":
    instance = UserManager()
    instance.createUser("alyssach") 
    test = instance.getUser("alyssach")
    print test.getName()
    instance.createUser("alyssach")
    instance.createUser("eaheaton")

