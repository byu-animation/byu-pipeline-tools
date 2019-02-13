import time

def timestampThisYear():
	millis = long(time.time())
	firstJan2017 = 1483254000
	return millis - firstJan2017
