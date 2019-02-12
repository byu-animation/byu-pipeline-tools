import hou
import sys, os
from byuam.environment import Project, Department
from byuam.body import Body, Asset, Shot, AssetType
from byugui import CheckoutWindow, message_gui

this = sys.modules[__name__]

project = Project()
environment = Environment()

# The source HDA's are currently stored inside the pipe source code.
hda_path = os.path.join(environment.get_project_dir(), "byu-pipeline-tools", "houdini-tools", "otls")

# TODO: Create Hair and Cloth digital assets.
# These are a bunch of HDA's to copy each time you create a new material, hair, etc.
hda_definitions = {
    Department.MATERIAL: hou.hdaDefinition(hou.sopNodeTypeCategory(), "byu_material", os.path.join(hda_path, "byu_material.hda")),
    Department.MODIFY: hou.hdaDefinition(hou.sopNodeTypeCategory(), "byu_modify", os.path.join(hda_path, "byu_modify.hda")),
    Deparment.HAIR: hou.hdaDefinition(hou.objNodeTypeCategory(), "byu_hair", os.path.join(hda_path, "byu_hair.hda")),
    Department.CLOTH: hou.hdaDefinition(hou.objNodeTypeCategory(), "byu_cloth", os.path.join(hda_path, "byu_cloth.hda"))
}

'''
    This function tabs in a BYU Set and fills its contents with other BYU Geo nodes based on JSON data
'''
def byu_set(parent, set_name):
    return None

'''
    This function tabs in a BYU Character node and fills its contents with the appropriate character name.
    Departments is a mask because sometimes we tab this asset in when we want to work on Hair or Cloth, and don't want the old ones to be there.
'''
def byu_character(parent, asset_name, departments=[Department.MATERIAL, Department.MODIFY, Department.HAIR, Department.CLOTH]):

    # Set up the body/elements and make sure it's a character
    body = this.project.get_body(asset_name)
    if not body.is_asset() or not body.get_type() == AssetType.CHARACTER:
        message_gui.error("Must be a character.")
        return None
    node = parent.createNode("byu_character")
    node.setName(asset_name.title(), unique_name=True)
    node.parm("character").set(asset_name)

    # Set the contents to the character's nodes
    set_contents_character(node, asset_name)

    return node

'''
    This function sets the inner contents of a BYU Character node.
'''
def set_contents_character(node, asset_name, departments=[Department.MATERIAL, Department.MODIFY, Department.HAIR, Department.CLOTH]):
    # Set up the body/elements and make sure it's a character. Just do some simple error checking.
    body = this.project.get_body(asset_name)
    if not body.is_asset() or body.get_type() != AssetType.CHARACTER or "byu_character" not in node.type().name():
        message_gui.error("Must be a character.")
        return None
    elements = body.list_elements()
    inside = node.node("inside")

    # Make sure the geo is set correctly
    geo = inside.node("geo")
    if geo is None:
        # Send in the department list, but exclude the hair and cloth departments
        geo = byu_geo(inside, asset_name, (d for d in departments if d != Department.HAIR and d != Department.CLOTH))
    set_contents_geo(asset_name, geo)

    # Make sure the correct hair node is tabbed in, or none if doesn't exist
    hair = inside.node("hair")
    if Department.HAIR is in elements and Department.HAIR is in departments:
        # Delete the old one
        if hair is not None:
            hair.destroy()
        # This line checks to see if an HDA matches this name. If not, you probably need to create one or reload your HIP file.
        if hou.preferredNodeType("Object/" + asset_name + "_" + Department.HAIR) is not None:
            hair = inside.createNode(asset_name + "_" + Department.HAIR)
            hair.setName()
            hair.setInput(0, geo)
    elif hair is not None:
        # Delete the old one
        hair.destroy()

    # Make sure the correct cloth node is tabbed in, or none if doesn't exist
    cloth = inside.node("cloth")
    if Department.CLOTH is in elements and Department.CLOTH is in departments:
        # Delete the old one
        if cloth is not None:
            cloth.destroy()
        # This line checks to see if an HDA matches this name. If not, you probably need to create one or reload your HIP file.
        if hou.preferredNodeType("Object/" + asset_name + "_" + Department.CLOTH) is not None:
            cloth = inside.createNode(asset_name + "_" + Department.CLOTH)
            cloth.setInput(0, geo)
    elif cloth is not None:
        # Delete the old one
        cloth.destroy()

    inside.layoutChildren()
    return node

'''
    This function tabs in a BYU Geo node and fills its contents according to the appropriate asset name.
'''
def byu_geo(parent, asset_name, departments=[Department.MATERIAL, Department.MODIFY]):
    # Set up the body/elements and check if it's an asset.
    body = this.project.get_body(asset_name)
    if not body.is_asset():
        message_gui.error("Must be an asset.")
        return None
    elements = body.list_elements()

    # Set up the nodes, name geo
    node = parent.createNode("byu_geo")
    if "byu_character" in parent.type().name():
        node.setName("geo")
    else:
        node.setName(asset_name.title(), unique_name=True)

    # Set the contents to the nodes that belong to the asset
    set_contents_geo(node, asset_name)

    return node

'''
    This function sets the dynamic inner contents of a BYU Geo node.
'''
def set_contents_geo(node, asset_name, departments=[Department.MATERIAL, Department.MODIFY]):
    # Set up the body/elements and make sure it's a character. Just do some simple error checking.
    body = this.project.get_body(asset_name)
    if not body.is_asset() or body.get_type() == AssetType.SET or "byu_geo" not in node.type().name():
        message_gui.error("Must be a prop or character.")
        return None
    inside = node.node("inside")
    shot_modeling = inside.node("shot_modeling")

    # Make sure the correct modify node is tabbed in, or none if doesn't exist
    modify = inside.node("modify")
    if Department.MODIFY is in elements and Department.MODIFY is in departments:
        # Delete the old one
        if modify is not None:
            modify.destroy()
        # This line checks to see if an HDA matches this name. If not, you probably need to create one or reload your HIP file.
        if hou.preferredNodeType("Sop/" + asset_name + "_" + Department.MODIFY) is not None:
            shot_modeling_input = shot_modeling.inputs()[0]
            modify = inside.createNode(asset_name + "_" + Department.MODIFY)
            modify.setInput(0, shot_modeling_input)
            shot_modeling.setInput(0, modify)
    elif modify is not None:
        # Delete the old one
        modify.destroy()

    # Make sure the correct material node is tabbed in, or none if doesn't exist
    material = inside.node("material")
    if Department.MATERIAL is in elements and Department.MATERIAL is in departments:
        # Delete the old one
        if material is not None:
            material.destroy()
        # This line checks to see if an HDA matches this name. If not, you probably need to create one or reload your HIP file.
        if hou.preferredNodeType("Sop/" + asset_name + "_" + Department.MATERIAL) is not None:
            shot_modeling_input = shot_modeling.inputs()[0]
            material = inside.createNode(asset_name + "_" + Department.MATERIAL)
            material.setInput(0, shot_modeling_input)
            shot_modeling.setInput(0, material)

    inside.layoutChildren()

#TODO: Allow the manual creation of any HDA for any Character or Prop

def create_hda(body_name, department):
    # Gather information about the publish
    body = this.project.get_body()
    element = Element()
    if department not in body.list_elements():
        element = body.create_element(department)
    else:
        element = body.get_element(department)
    username = project.get_current_username()

    # If it's an asset, create the appropriate nodes
    if body.is_asset():
         checkout_file = element.checkout(username)

         if body.get_type() == AssetType.SET:
             message_gui.error("Asset must be a PROP or CHARACTER.")
             return
         if body.get_type() == AssetType.PROP and (department == Department.HAIR or department == Department.CLOTH):
             message_gui.error("Hair and cloth can only be made for characters.")
             return


         higher_operator_name = "byu_character" if body.get_type() == AssetType.CHARACTER else "byu_geo"
         higher_operator = tab_in_asset(higher_operator_name)
         inside = higher_operator.node("inside")

         # CREATE NEW HDA DEFINITION
         operator_name = element.get_parent() + "_" + element.get_department()
         operator_label = (asset.get_name().replace("_", " ") + " " + element.get_department()).title()
         hda = this.hda_definitions[department].copyToHDAFile(checkout_file, operator_name, operator_label)
         assetTypeDef = hda.type().definition()
         assetTypeDef.setIcon(environment.get_project_dir() + '/byu-pipeline-tools/assets/images/icons/hda-icon.png')




        # Checkout assembly
    else:
        message_gui.error("Must be an asset of type PROP or CHARACTER.")
        return

#TODO: Decide whether or not we'll have an automated script for the rest of it.
# -----------------------
# Idea: it's only partially automated. You pick the asset, it'll convert it and tab it into your scene. Then you decide if you
#   want to publish it or not.
# -----------------------
# Idea: We can check the old import assets for if there's anything between the switch node and the output. If there is,
#   package it up into a modify digital asset. It might include primvars, but who cares.
# -----------------------
# Idea: we can automatically package up the shopnet as a material node. I don't think we'll be able to distinguish enough
#   to be able to automatically fill primvars in. But yeah.
# -----------------------

def convert_all_bodies():
    for asset in this.project.list_assets():
        print ("currently processing: ", asset, "\n")
        body = this.project.get_body(asset)
        elements = body.list_elements()
        if Department.MATERIAL is in elements:
        else:
            body.create_element(Department.MATERIAL)
