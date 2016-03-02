#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  user.py
#  
#  Copyright 2016 Alyssa Heaton 
#  

import pwd

'''
The User class holds information about a user, this will be used a lot more for the web site 
'''
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



'''
The UserManager class holds the list of users for the pipleine.  
'''
class UserManager:    
    
    USERLIST = []
    
    def __init__(self):
        self.USERLIST = []
        
    '''
    Returns a user object based on a given CSID. If there is no users then 
    it returns the string "Empty list".  If no user is found then the sting
    "No such user".  If the user is found then it returns the user object
    '''     
    def getUser(self, CSID):
		
		if len(self.USERLIST) == 0:
			return "Empty list"
		
		for i in range(len(self.USERLIST)):
			if self.USERLIST[i].getCSID() == CSID:
				return self.USERLIST[i]
		return "No such user"       
       
    '''
    Creates a user based on a given CSID.  If an invalid CSID is given the function will break
    '''   
    def createUser(self, newCSID):     
        
        tester = self.getUser(newCSID)
        if tester == "No such user" or tester == "Empty list":
			#print "user already exists"
		 
			CSID = newCSID
			userInfo = pwd.getpwnam(newCSID)
			FULLNAME = userInfo.pw_gecos
			NAME = FULLNAME
			EMAIL = "DEFALT"
			self.USERLIST.append(User(CSID, NAME, EMAIL))


