import glob
import json
import os
import re
import smtplib
import time

def readfile(filepath):
	"""
	reads a pipeline json file and returns the resulting dictionary
	"""
	with open(filepath, "r") as json_file:
		json_data = json.load(json_file)

	return json_data

def writefile(filepath, datadict):
	"""
	writes the given data dictionary to a pipeline json file at the given filepath
	"""
	tmp_name, tmp_ext = os.path.splitext(filepath)
	tmp_filepath = tmp_name+"_tmp"+tmp_ext
	with open(tmp_filepath, "w") as json_file:
		json.dump(datadict, json_file, indent=0)
	os.rename(tmp_filepath, filepath)

def mkdir(dirpath):
	"""
	create the given filepath. returns true if successful, false otherwise.
	"""
	try:
		os.mkdir(dirpath) # TODO: ensure correct permissions
		os.chmod(dirpath, 0777)
	except OSError as e:
		return False # file already exists
	return True

def version_file(filepath, zero_pad=3):
	"""
	versions up the given file based on other files in the same directory. The given filepath
	should not have a version at the end. e.g. given "/tmp/file.txt" this function will return
	"/tmp/file000.txt" unless there is already a file000.txt in /tmp, in which case it will
	return "/tmp/file001.txt". zero_pad specifies how many digits to include in the version
	number--the default is 3.
	"""
	if zero_pad < 1:
		zero_pad = 1
	dirpath, filename = os.path.split(filepath)
	base, ext = os.path.splitext(filename)
	searchpath = os.path.join(dirpath, "*")
	files = glob.glob(searchpath)
	versions = []
	for f in files:
		tmpname = os.path.basename(f)
		if re.match(base+"[0-9]{%d}"%zero_pad+ext, tmpname):
			versions.append(tmpname)
	versions.sort()
	version_num = 0
	if len(versions) > 0:
		latest = versions[-1]
		latest_name = os.path.splitext(latest)[0]
		idx = len(latest_name) - zero_pad
		num_str = latest_name[idx:]
		version_num = int(num_str)+1
	return os.path.join(dirpath, base+str(version_num).zfill(zero_pad)+ext)

def version_dir(dirpath, zero_pad=3):
	"""
	versions up the given directory based on other directories in the same directory. The given dirpath
	should not have a version at the end. e.g. given "/tmp/v" this function will return
	"/tmp/v000" unless there is already a v000 dir in /tmp, in which case it will
	return "/tmp/v001". zero_pad specifies how many digits to include in the version
	number--the default is 3.
	"""
	raise NotImplementedError() # TODO

def alphanumeric(name):
	"""
	returns a string of the same length as the given name with all the non-alphanumeric characters
	replaced by underscores and all uppercase letters replaced by lowercase letters
	name -- string to make alphanumeric
	"""
	seq = []
	for char in name:
	    if not char.isalnum():
	        seq.append('_')
	    else:
	        seq.append(char)

	return ''.join(seq).lower()

def timestamp():
	"""
	return a string containing the current time
	"""
	return time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime())

def sendmail(dst_addresses, subject, message, src_address, password, src_name=""):
	"""
	sends an email to the given email addresses, with the given subject and message, from the given
	gmail account that has the given password (must be a gmail account). Return True if successful.
	dst_addresses -- list of strings destination email addresses
	subject -- string email subject line
	message -- string email message
	src_address -- string gmail account to send email from,
				   this account must have allowed "less secure app access"
	password -- string password to the src_address account
	src_name -- string (optional) name of the src_address account
	"""

	email = "From: %s <%s>\nSubject: %s\n\n%s" % (src_name, src_address, subject, message)
	client = smtplib.SMTP("smtp.gmail.com", 587)
	client.ehlo()
	client.starttls() #TODO: add keyfile
	client.ehlo()
	success = True
	try:
		client.login(src_address, password)
		client.sendmail(src_address, dst_addresses, email)
	except (smtplib.SMTPAuthenticationError, smtplib.SMTPRecipientsRefused) as error:
		sucess = False
	client.close()
	return success
