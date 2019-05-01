import os,sys,subprocess
sys.path.insert(0,'../shelf/scripts')
import checkout
from byuam import Body,AssetType,Department,Element,Project,Environment
import json_exporter_non_gui
import traceback

import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds

def audit():
    project=Project()
    environment=Environment()


    asset_dir=project.get_assets_dir()


    for i,asset in enumerate(project.list_assets(AssetType.PROP)):

        asset_obj=project.get_body(asset)
        element_obj = asset_obj.get_element(Department.MODEL,force_create=True)
        element_path = element_obj.checkout(environment.get_current_username())
        #cmds.file(rename='/tmp/lol'+str(i)+'.mb')
        #cmds.file(save=True)
        checkout.non_gui_open(element_path,asset)

    print 'Done'

def json_audit():
    project=Project()
    environment=Environment()


    asset_dir=project.get_assets_dir()

    failed_str = ""
    for i,asset in enumerate(project.list_assets(AssetType.PROP)):

        try:
            asset_obj=project.get_body(asset)
            element_obj = asset_obj.get_element(Department.MODEL,force_create=True)
            element_path = element_obj.checkout(environment.get_current_username())
            checkout.non_gui_open(element_path, asset)
            json_exporter_non_gui.exportProp(asset_obj)
        except Exception, err:
            error_str = ""
            error_str += "\nError exporting JSON for {0}".format(asset)
            error_str += "\n" + traceback.format_exc()
            print error_str

            failed_str += error_str
            continue

    print failed_str
    with open(os.environ['BYU_TOOLS_DIR'] + "pipe_audit_log.txt", 'w+') as f:
        f.write(failed_str)
        f.close()

json_audit()
