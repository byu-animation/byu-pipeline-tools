import hou
import os
# import pyqt_houdini
from PyQt4 import QtGui, QtCore

from byuam import Department, Project
from byugui import CheckoutWindow

def assemble_hda():
    asset_name = checkout_window.current_item

    project = Project()
    username = project.get_current_username()
    asset = project.get_asset(asset_name)
    
    assembly = asset.get_element(Department.ASSEMBLY)
    checkout_file = assembly.checkout(username)

    element = asset.get_element(Department.MODEL)
    cache = element.get_cache_dir()
    cache = cache.replace(project.get_project_dir(), '$JOB')
    # TODO: only load files whose extension matches element.get_cache_ext()
    geo_files = [x for x in os.listdir(element.get_cache_dir()) if not os.path.isdir(x)]

    obj = hou.node('/obj')
    subnet = obj.createNode('subnet')
    for geo_file in geo_files:
        geo = subnet.createNode('geo')
        for child in geo.children():
            child.destroy()
        abc = geo.createNode('alembic')
        geo_file_path = os.path.join(cache, geo_file)
        abc.parm('fileName').set(geo_file_path)
        name = ''.join(geo_file.split('.')[:-1])
        geo.setName(name, unique_name=True)

    subnet.setName(asset_name, unique_name=True)

    # TODO: broken for now, need bug fix from sidefx
    # subnet.createDigitalAsset(name=assembly.get_long_name(), hda_file_name=checkout_file, description=asset_name)

    # subnet.type().definition().copyToHDAFile(checkout_file, new_name=assembly.get_long_name(), new_menu_name=asset_name)
    # hou.hda.installFile(checkout_file)

def go():
    # checkout_window = CheckoutWindow()
    # app = QtGui.QApplication.instance()
    # if app is None:
    #     app = QtGui.QApplication(['houdini'])
    global checkout_window
    checkout_window = CheckoutWindow(hou.ui.mainQtWindow(), [Department.ASSEMBLY])
    checkout_window.finished.connect(assemble_hda)    

    # asset_name = 'hello_world'
    # asset = project.get_asset(asset_name)
    
    