import hou, sys, os, json
from byuam import Project, Department, Element, Environment, Body, Asset, Shot, AssetType
from byugui import message_gui
from byugui.item_list import SelectFromList
import assemble_v2

global select_from_list_dialog

def go():
    global select_from_list_dialog
    select_from_list_dialog = SelectFromList()
    select_from_list_dialog.setWindowTitle("Select shot")
    select_from_list_dialog.setList(Project().list_shots())
    select_from_list_dialog.selected.connect(import_shot)
    select_from_list_dialog.show()

def import_shot(shot_name):

    # Bring in the body so we can get info
    body = Project().get_body(shot_name)
    if not body or not body.is_shot():
        message_gui.error("Error with body.")
        return

    # Bring in element so we can get cache directory
    element = body.get_element(Department.ANIM)
    if not element:
        message_gui.error("Anim department does not exist for {0} ".format(shot_name))
        return

    cache_dir = element.get_cache_dir()

    sets_json = []
    characters_json = []
    animated_props_json = []

    try:
        with open(os.path.join(cache_dir, "sets.json")) as f:
            sets_json = json.load(f)
    except Exception as error:
        print "{0}/sets.json not found.".format(cache_dir)

    try:
        with open(os.path.join(cache_dir, "characters.json")) as f:
            characters_json = json.load(f)
    except Exception as error:
        print "{0}/characters.json not found.".format(cache_dir)

    try:
        with open(os.path.join(cache_dir, "animated_props.json")) as f:
            animated_props_json = json.load(f)
    except Exception as error:
        print "{0}/animated_props.json not found.".format(cache_dir)

    set_nodes = []
    character_nodes = []
    animated_prop_nodes = []

    for set in sets_json:
        try:
            set_node = assemble_v2.tab_in(hou.node("/obj"), set["asset_name"])
        except:
            print "Error with {0}".format(set)
            continue
        set_nodes.append(set_node)
        for prop in set_node.children():
            data_parm = prop.parm("data")
            if data_parm is None:
                continue
            data = data_parm.evalAsJSONMap()
            for animated_prop in animated_props_json:
                if data["asset_name"] == animated_prop["asset_name"] and data["version_number"] == animated_prop["version_number"]:
                    prop.parm("space").set("anim")
                    prop.parm("shot").set(shot_name)
                    animated_prop_nodes.append(prop)

    print "we started from the bottom now we here"
    print "\tCharacters: {0}".format(characters_json)
    for character in characters_json:
        #TODO: Hardcoded name of show
        if character["asset_name"] == "dand_camera":
            camera_node = tab_in_camera(shot_name)
            character_nodes.append(camera_node)
            continue
        try:
            character_node = assemble_v2.byu_character(hou.node("/obj"), character["asset_name"],shot=shot_name)
            character_nodes.append(character_node)
        except:
            print "Error with {0}".format(character)
            continue
        #shot_parm = character_node.parm("shot")
        #shot_parm.set(shot_name)

        data_parm = character_node.parm("data")
        data = data_parm.evalAsJSONMap()
        print character
        print character["version_number"]
        data["version_number"] = str(character["version_number"])
        data_parm.set(data)

        version_number_parm = character_node.parm("version_number")
        version_number_parm.set(character["version_number"])

    box = hou.node("/obj").createNetworkBox()
    box.setComment(shot_name)
    for set_node in set_nodes:
        box.addItem(set_node)
    for character_node in character_nodes:
        box.addItem(character_node)
    for animated_prop_node in animated_prop_nodes:
        box.addItem(animated_prop_node)
    for set_node in set_nodes:
        set_node.moveToGoodPosition()
    for character_node in character_nodes:
        character_node.moveToGoodPosition()
    for animated_prop_node in animated_prop_nodes:
        character_node.moveToGoodPosition()

    #hou.node("/obj").layoutChildren()

def tab_in_camera(shot_name):
    camera_node = hou.node("/obj").createNode("byu_camera")
    camera_node.parm("shot").set(shot_name)
    return camera_node
