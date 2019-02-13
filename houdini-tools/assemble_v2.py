'''

    Hunter Tinney

    ================
    Intro to Pipe V2
    ================

    I designed this new procedure to minimize dependencies and allow for easier changes to our Houdini pipeline. With the old
    code, whenever we assembled an asset, we were locked into a specific configuration for that asset and would need to
    re-assemble if anything changed. Now, we abstracted out a lot of the functionality into nodes like BYU Import, BYU Geo,
    BYU Character, BYU Set, etc, so that way we push changes to all the assets at once (for example, if we were to switch to
    USD mid production.)

    Please pay attention to the differences in each of these nodes. Functional HDAs and Template HDAs are very different (for
    example, a Content HDA is never intended to be tabbed into Houdini, it simply serves as a template for creating other
    HDAs.)


    =======================
    Dynamic Content Subnets
    =======================

    These HDAs are simply subnets that hold other HDAs. The difference is that they will destroy and re-tab in the HDAs inside
    of them, based on what asset is loaded. Let's say Swingset_001 is loaded, and we switch to Swingset_002. BYU Geo would
    switch out all the Content HDAs (material, etc.) of Swingset_001 with the content of Swingset_002. A description of
    Content HDAs is found in the "Content HDAs" section.

        NAME         Subnet Type    Description
     ----------------------------------------------------------------------------------------------------------------------------
    | BYU Geo          OBJ>SOP    Houses the other nodes at the most basic level, good enough for props and character meshs.     |
    | BYU Character    OBJ>OBJ    Houses a BYU Geo, a Hair asset and a Cloth asset. It's our verion of a character group.        |
    | BYU Set          OBJ>OBJ    Reads from a JSON file (exported from Maya) that contains positions of assets in a set. It     |
    |                                 tabs them all in as BYU Geos, and then offsets them to their correct                       |
    |                                 positions/scales/rotates.                                                                  |
     ----------------------------------------------------------------------------------------------------------------------------


    ===============
    Functional HDAs
    ===============

    These HDAs take some of the more common procedures and generalize them. That way, if we ever change the way we import
    geometry into Houdini, we could make a simple change to BYU Import (for example) and that change would propagate to all
    the assets that contain BYU Import.

        NAME         Node Type    Description
     ----------------------------------------------------------------------------------------------------------------------------
    | BYU Import       SOP        Has all the functionality to bring in assets from the pipe via Alembic. This functionality     |
    |                                 could be swapped out for USD Import at a future date.                                      |
    | BYU Mat. Assign  SOP        Full Name: BYU Material Assign. Basically the Material SOP, but provides a way of switching    |
    |                                 between material options.                                                                  |
    | BYU Shopnet      SOP        Provides a way for us to supply default material setups for shading artists.                   |
    | BYU Primvars     SOP        Allows for quick selection of primitive/point/vertex groups and using them as masks for        |
    |                                 RenderMan shaders.                                                                         |
     ----------------------------------------------------------------------------------------------------------------------------


    =============
    Template HDAs
    =============

    These HDAs are created on an as-needed basis for each asset in the pipe (although most assets will have a material.) They
    are created by duplicating the template HDA (which is stored in the houdini-tools package.) We store that HDA in the User
    folder of the artist. Then, when they are ready, we publish it to the pipe as a new HDA. Because it is a new HDA definition,
    we are locked into its functionality unless the asset is re-created. This is a bit unfortunate (it is the equivalent to
    copying and pasting similar code instead of abstracting it out into a shared function/class.) However, we have ensured that
    most of the functionality that we would like to tweak has been abstracted out into Functional HDAs that are inside each of
    these nodes. That way, if we change the functional HDAs, we will propagate those changes to all the Content HDAs that
    contain them. If you find a better way to emulate polymorphism in HDAs, please update this!!

        NAME         Node Type    Description
     ----------------------------------------------------------------------------------------------------------------------------
    | BYU Material     SOP         Holds a Primvars, Mat. Assign and Shopnet Functional HDA. Intended for shading.                |
    | BYU Modify       SOP         Modifies incoming geometry, intended for any geometry fixes that need to be done in Houdini.   |
    | BYU Hair         OBJ>OBJ     Holds all hair subnets for a given character. It should take a BYU Geo as an input. It should  |
    |                                  also have simulation parameters promoted to the top-level, which is done by the artist.    |
    | BYU Cloth        OBJ>OBJ     Holds all cloth subnets for a given character. It should take a BYU Geo as an input. It should |
    |                                  also have simulation parameters promoted to the top-level, which is done by the artist.    |
     ----------------------------------------------------------------------------------------------------------------------------

    ============
    Content HDAs
    ============

    Content HDAs are simply instances of Template HDAs. They could be materials, modifies, hair subnets, cloth subnets, etc.


'''
import hou
import sys, os
from byuam import Project, Department, Environment, Body, Asset, Shot, AssetType
from byugui import CheckoutWindow, message_gui

# I set this sucker up as a singleton. It's a matter of preference.
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
    Department.HAIR: hou.hdaDefinition(hou.objNodeTypeCategory(), "byu_hair", os.path.join(hda_path, "byu_hair.hda")),
    Department.CLOTH: hou.hdaDefinition(hou.objNodeTypeCategory(), "byu_cloth", os.path.join(hda_path, "byu_cloth.hda"))
}


'''
    Script accessed by toolscripts
'''
def tab_in(parent, asset_name, departments=[Department.MATERIAL, Department.MODIFY, Department.HAIR, Department.CLOTH]):
    body = this.project.get_body()
    if body is None or not body.is_asset():
        message_gui.error("Pipeline error: This asset either doesn't exist or isn't an asset.")
        return
    if body.type() == AssetType.CHARACTER:
        return byu_character(parent, asset_name, departments)
    elif body.type() == AssetType.PROP:
        return byu_geo(parent, asset_name, departments)
    elif body.type() == AssetType.SET:
        return byu_set(parent, asset_name)
    else:
        message_gui.error("Pipeline error: this asset isn't a character, prop or set.")
        return


'''
    This function tabs in a BYU Set and fills its contents with other BYU Geo nodes based on JSON data
'''
def byu_set(parent, set_name):

    parent.createNode("byu_set")
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
    elements = [d for d in body.default_departments() if len(body.list_elements(d)) > 0]
    inside = node.node("inside")

    # Make sure the geo is set correctly
    geo = inside.node("geo")
    if geo is None:
        # Send in the department list, but exclude the hair and cloth departments
        geo = byu_geo(inside, asset_name, (d for d in departments if d != Department.HAIR and d != Department.CLOTH))
    set_contents_geo(asset_name, geo)

    # Make sure the correct hair node is tabbed in, or none if doesn't exist
    hair = inside.node("hair")
    if Department.HAIR in elements and Department.HAIR in departments:
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
    if Department.CLOTH in elements and Department.CLOTH in departments:
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
    elements = [d for d in body.default_departments() if len(body.list_elements(d)) > 0]

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
    print body
    if body is None:
        message_gui.error("Asset doesn't exist.")
        return None
    if not body.is_asset() or body.get_type() == AssetType.SET or "byu_geo" not in node.type().name():
        message_gui.error("Must be a prop or character.")
        return None
    elements = [d for d in body.default_departments() if len(body.list_elements(d)) > 0]
    importnode = node.node("import")
    inside = node.node("inside")
    shot_modeling = inside.node("shot_modeling")

    # Set the asset_name and reload
    if node.parm("literal").evalAsString() != asset_name:
        node.parm
    importnode.parm("reload").pressButton()

    # Make sure the correct modify node is tabbed in, or none if doesn't exist
    modify = inside.node("modify")
    if Department.MODIFY in elements and Department.MODIFY in departments:
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

    # TODO: On all of these, if someone is working on them (aka, they're checked out) give an error message.
    # Make sure the correct material node is tabbed in, or none if doesn't exist
    material = inside.node("material")
    if Department.MATERIAL in elements and Department.MATERIAL in departments:
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
    elements = [d for d in body.default_departments() if len(body.list_elements(d)) > 0]
    if department not in elements:
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
        elements = [d for d in body.default_departments() if len(body.list_elements(d)) > 0]
        if Department.MATERIAL in elements:
            print("yay")
        else:
            body.create_element(Department.MATERIAL)
