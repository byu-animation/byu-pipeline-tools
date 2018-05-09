from byuam.environment import Department
from byugui import selection_gui, message_gui
from byuam.body import AssetType
from PySide2 import QtWidgets
from byuam import Project

import pymel.core as pm
import os
import json
import tempfile
import sketchFab as sfu
import maya.cmds as cmds
import sketchFab.requests as requests
import maya.mel as Mm
from maya import OpenMayaUI as omui
from maya import OpenMaya as om
from time import sleep

SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v3/models'.format(SKETCHFAB_DOMAIN)
SKETCHFAB_MODEL_URL = 'https://{}/models/'.format(SKETCHFAB_DOMAIN)
API_TOKEN = '2ec3de9f1bb54facb7832d44f492300f'

def go(element=None, dept=None):

	pm.loadPlugin('fbxmaya.so')
	if not pm.sceneName() == '':
		pm.saveFile(force=True)

	if element is None:
		filePath = pm.sceneName()
		fileDir = os.path.dirname(filePath)
		proj = Project()
		checkout = proj.get_checkout(fileDir)
		# Make sure we have access to element data for this asset
		if checkout is None:
			parent = QtWidgets.QApplication.activeWindow()
			element = selection_gui.getSelectedElement(parent)
			if element is None:
				print 'There is nothing checked out.'
				return None
		else:
			body_name = checkout.get_body_name()
			dept_name = checkout.get_department_name()
			elem_name = checkout.get_element_name()
			body = proj.get_body(body_name)
			element = body.get_element(dept_name, name=elem_name)

	#Get the element from the right Department
	if dept is not None and not element.get_department() == dept:
		print 'We are overwriting the', element.get_department(), 'with', dept
		body = proj.get_body(element.get_parent())
		element = body.get_element(dept)

	if element is None:
		print "Nothing is selected."
		return

	if not element.get_department() == Department.MODEL:
		print "We can only publish models to sketchFab (no rigs)."
	else:
		export(element)

def export(element):
	proj = Project()
	body_name = element.get_parent()
	body = proj.get_body(body_name)
	asset_file_path = element.get_dir()
	uid_file_path = '{0}/{1}.json'.format(asset_file_path, body_name)
	print uid_file_path
	republish = os.path.exists(uid_file_path)

	fbx_file = prepare_files(body_name)

	data = None
	model_uid = ''

	if republish:
		with open(uid_file_path) as uid_file:
			uid_file_data = json.load(uid_file)
		model_uid = uid_file_data['uid']
		data = republish_existing_asset(body.get_name(), body.get_description(), model_uid)
	else:
		data = publish_new_asset(body.get_name(), body.get_description())

	f = open(fbx_file, 'rb')

	files = {
        'modelFile': f
    }

	try:
		model_uid = upload_to_sketchfab(data, files, republish, model_uid)
		#poll_processing_status(model_uid)
	finally:
		f.close()

	if not model_uid is None and len(model_uid) > 0 and not republish:
		uid_data = {
            'uid': model_uid
        }
		with open(uid_file_path, 'w') as outfile:
			json.dump(uid_data, outfile)

def prepare_files(body_name):
	# create a temporary directory
    tmp_dir = tempfile.mkdtemp()
    base_name = os.path.join(tmp_dir, body_name)
    fbx_file = '{0}.fbx'.format(base_name)

	# Set options
	# Force textures embedding
    Mm.eval('FBXExportEmbeddedTextures -v true')
	# Force binary fbx export (smaller size)
    Mm.eval('FBXExportInAscii  -v false')

    # for some reason Maya fails to export to this location when the file does not yet exist
    # create a dummy file with zero length that has the same name
    open(fbx_file, 'w').close()
    # export Maya scene as FBX
    cmds.file(fbx_file, force=True, exportAll=True, preserveReferences=True, type='FBX export')
    # create a screen shot and save as .png
    thumb_file_name = '%s.png' % base_name
    buffer = om.MImage()
    omui.M3dView.active3dView().readColorBuffer(buffer, True)
    buffer.resize(448, 280, True)
    buffer.writeToFile(thumb_file_name, 'png')

    return fbx_file

def publish_new_asset(name, description):
    private = 0
    autopublish = 1
    password = ''
    tags = ''
    maya_version = cmds.about(version=True).replace(' ', '_')

    global API_TOKEN
    data = {
        'token': API_TOKEN,
        'name': name,
        'description': description,
        'tags': tags,
        'private': private,
        'isPublished': autopublish,
        'password': password,
        'source': 'maya-' + maya_version
    }

    return data


def republish_existing_asset(name, description, model_uid):
    private = 0
    autopublish = 1
    password = ''
    tags = ''
    maya_version = cmds.about(version=True).replace(' ', '_')

    global API_TOKEN
    data = {
        'token': API_TOKEN,
        'uid': model_uid,
        'name': name,
        'description': description,
        'tags': tags,
        'private': private,
        'isPublished': autopublish,
        'password': password,
        'source': 'maya-' + maya_version
    }

    return data

def upload_to_sketchfab(data, files, republish=False, uid=None):
	try:
		r = None
		global SKETCHFAB_API_URL
		if republish:

			putURL = '{0}/{1}'.format(SKETCHFAB_API_URL, uid)
			r = requests.put(putURL, **_get_request_payload(
                data, files=files))
		else:
			r = requests.post(SKETCHFAB_API_URL, data=data, files=files, verify=False)
	except requests.exceptions.RequestException as e:
		print 'An error occured: {}'.format(e)
		return

	result = None

	try:
		result = r.json()
		if r.status_code != requests.codes.created:
			print 'Upload failed with error: {}'.format(result)
			return
	except ValueError:
		print "There was an error reading the result from the server"

	global SKETCHFAB_MODEL_URL
	model_uid = uid
	model_url = ''
	if not result is None:
		model_uid = result['uid']
	if not model_uid is None:
		model_url = SKETCHFAB_MODEL_URL + model_uid
	print 'Upload successful. Your model is being processed.'
	print 'Once the processing is done, the model will be available at: {}'.format(model_url)

	if model_uid == None:
		return uid
	else:
		return model_uid

def poll_processing_status(model_uid):
	if model_uid is None:
		return

	global SKETCHFAB_API_URL
	global API_TOKEN
	polling_url = '{}/{}/status?token={}'.format(SKETCHFAB_API_URL, model_uid, API_TOKEN)
	polling_url = '{}/{}'.format(SKETCHFAB_API_URL, model_uid)
	max_errors = 10
	errors = 0
	retry = 0
	max_retries = 15
	retry_timeout = 5 # seconds

	while (retry < max_retries) and (errors < max_errors):
		print 'Try polling processing status (attempt #{}) ...'.format(retry)

		try:
			r = requests.get(polling_url)
		except requests.exceptions.RequestException as e:
			print 'Try failed with error {}'.format(e)
			errors += 1
			retry += 1
			continue

		try:
			result = r.json()
			error = result["status"]
			print result
		except ValueError:
			print "Error reading result from server. You probably are doing a bad HTTP request."
			errors += 1
			retry += 1
			continue
		except KeyError:
			print "JSON result from server:"
			print result
			print "The file with this ID:" + model_uid + " does not exist on the server."
			errors += 1
			retry += 1
			continue

		if r.status_code != requests.codes.ok:
			print 'Upload failed with error: {}'.format(result['status']['error'])
			errors += 1
			retry += 1
			continue

		processing_status = result['status']['processing']
		if processing_status == 'PENDING':
			print 'Your model is in the processing queue. Will retry in {} seconds'.format(retry_timeout)
			#print 'Want to skip the line? Get a pro account! https://sketchfab.com/plans'
			retry += 1
			#sleep(retry_timeout)
			continue
		elif processing_status == 'PROCESSING':
			print 'Your model is still being processed. Will retry in {} seconds'.format(retry_timeout)
			retry += 1
			#sleep(retry_timeout)
			continue
		elif processing_status == 'FAILED':
			print 'Processing failed: {}'.format(result['status']['error'])
			return
		elif processing_status == 'SUCCEEDED':
			global SKETCHFAB_MODEL_URL
			model_url = SKETCHFAB_MODEL_URL + model_uid
			print 'Model uploaded.'
			print model_url
			return

		retry += 1

	print 'Stopped polling after too many retries or too many errors'

def _get_request_payload(data={}, files={}, json_payload=False):
    """Helper method that returns the authentication token and proper content
    type depending on whether or not we use JSON payload."""
    global API_TOKEN
    headers = {'Authorization': 'Token {}'.format(API_TOKEN)}

    if json_payload:
        headers.update({'Content-Type': 'application/json'})
        data = json.dumps(data)

    return {'data': data, 'files': files, 'headers': headers}
