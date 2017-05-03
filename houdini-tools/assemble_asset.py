import hou
import os
# import pyqt_houdini
from PySide2 import QtGui, QtWidgets, QtCore

from byuam import Department, Project, Environment
from byugui import CheckoutWindow

def assemble_hda():
    asset_name = checkout_window.current_item

    project = Project()
    environment = Environment()
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

    hdaName = project.get_name() + "_" + asset_name
    subnet.setName(hdaName, unique_name=True)

    asset = subnet.createDigitalAsset(name=assembly.get_long_name())
    assetTypeDef = asset.type().definition()
    assetTypeDef.setIcon(environment.get_project_dir() + "/byu-pipeline-tools/assets/images/icons/hda-icon.png")

    # TODO: broken for now, need bug fix from sidefx
    # TODO: I think that the three lines above this should work. I don't know what all of this does. The extra option seem a little unnessary. and I dont' know why we need to copy the type properties. Shouldn't it be that those properties come over when we create the asset in the first place? Why on earth are we trying to install it? It should already show up for the user and he hasn't publihsed it yet so it shouldn't be published for anyone else yet. - Ben DeMann
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
