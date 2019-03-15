import os,sys,subprocess
sys.path.insert(0,'../shelf/scripts')
import checkout
from byuam import Body,AssetType,Department,Element,Project,Environment

import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds



project=Project()
environment=Environment()


asset_dir=project.get_assets_dir()


for i,asset in enumerate(project.list_assets(AssetType.PROP)):

    asset_obj=project.get_body(asset)
    element_obj = asset_obj.get_element(Department.MODEL,force_create=True)
    element_path = element_obj.checkout(environment.get_current_username())
    cmds.file(rename='/tmp/lol'+str(i)+'.mb')
    cmds.file(save=True)


    checkout.non_gui_open(element_path,asset)
print 'Done'
