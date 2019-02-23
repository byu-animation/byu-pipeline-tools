import hou, sys, os, json, assemble_v2
from byuam import Project, Department, Element, Environment, Body, Asset, Shot, AssetType, byu_xml
from byugui import CheckoutWindow, message_gui


global WINDOW
global DEPARTMENT

def add_callback():
    global WINDOW
    global DEPARTMENT

    name=WINDOW.current_item
    print name
    assemble_v2.create_hda(name,DEPARTMENT)

def add_hda(department):
    global WINDOW
    global DEPARTMENT
    DEPARTMENT=department[0]
    WINDOW =CheckoutWindow(hou.ui.mainQtWindow(),department)

    WINDOW.finished.connect(add_callback)


def xml_callBack():
    global WINDOW
    print WINDOW
    assetName=WINDOW.current_item
    print assetName
    try:
        byu_xml.writeXML(assetName)
        message_gui.message('Success, reload shelves to see asset')

    except Exception as e:
        print e.args
        message_gui.error('There was a problem',e.args)


def mass_xml():
    project=Project()

    errors=[]
    for asset in project.list_assets():
        try:
            byu_xml.writeXML(asset)

        except Exception as e:
            print asset
            errors.append(asset)

    if len(errors)>0:
        print 'failed generating xml for: ' + str(errors)

def make_xml():

    if len(hou.selectedNodes()) > 0:
        xml=[]
        errors=[]
        error=False
        for node in hou.selectedNodes():
            try:
                name=node.parm('data').evalAsJSONMap()['asset_name']
                byu_xml.writeXML(name)
                xml.append(name)
            except Exception as e:
                error=True
                errors.append(e.args)
                print e.args
        if error == True:
            message_gui.error('There was an issue generating xml for one of the selected nodes',str(errors))
        message_gui.message('Finished',  'Successfully generated XML for the following: '+str(xml))


    else:
        global WINDOW
        WINDOW=CheckoutWindow(hou.ui.mainQtWindow(),[Department.ASSEMBLY])
        WINDOW.finished.connect(xml_callBack)
