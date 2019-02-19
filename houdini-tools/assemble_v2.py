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
    example, a Template HDA is never intended to be tabbed into Houdini, it simply serves as a template for creating other
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

    These HDAs will never be tabbed in directly. They simply serve as template data that can be used to create other HDAs. Please
    see the section on "Content HDAs" below for an explanation of the process.

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

    Content HDAs are simply instances of Template HDAs. They could be materials, modify nodes, hair subnets, cloth subnets, etc.
    Typically their names will be something like "swingset_001_material". These HDAs are created on an as-needed basis for
    each asset in the pipe (although most assets will have a material.) They are created by duplicating the Template HDA
    (which is stored in the houdini-tools package.) We store that HDA in the User folder of the artist. Then, when they are ready,
    we publish it to the pipe as a new HDA. Because it is a new HDA definition, we are locked into its functionality unless the
    asset is re-created. This is a bit unfortunate (it is the equivalent to copying and pasting similar code instead of abstracting
    it out into a shared function/class.) However, we have ensured that most of the functionality that we would like to tweak has
    been abstracted out into Functional HDAs that are inside each of these nodes. That way, if we change the functional HDAs, we
    will propagate those changes to all the Content HDAs that contain them. If you find a better way to emulate polymorphism in
    HDAs, please update this!!


    ========
    Updating
    ========

    The different update modes have different meanings.

        smart: Sets will add new components, and delete old ones. Props and characters will update everything except checked out items and shot_modeling.

        clean: Everything is deleted and re-tabbed in, ensuring it is 100% synced. Does not allow for overrides.

        frozen: Nothing happens.

'''
import hou, sys, os, json
from byuam import Project, Department, Element, Environment, Body, Asset, Shot, AssetType
from byugui import CheckoutWindow, message_gui
# DEBUGGING ONLY
import signal
#import inspect
import datetime

def sigterm_handler(signal, frame):
    # TODO: Implement this
    # get the time
    # get tracebacks via http://docs.python.org/library/sys.html#sys.exc_info
    #    and http://docs.python.org/library/traceback.html
    #
    # Attempt to write all of the above to a file
    with open(os.path.join(Project().get_users_dir(), Project().get_current_username(), "houdini_log.txt"), "a+") as f:
        f.write(str(datetime.datetime.now()))
        f.write(str(sys.exc_info()))
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)


def lineno():
    return "nah"
    #return inspect.currentframe().f_back.f_lineno
def method_name():
    return "nah"
    #return sys._getframe(1).f_code.co_name
def super_print(message):

    with open(os.path.join(Project().get_users_dir(), Project().get_current_username(), "houdini_log.txt"), "a+") as f:
        print(message)
        #f.write("\n" + str(datetime.datetime.now()) + "\n")
        f.write(message)
# DEBUGGING END

# I set this sucker up as a singleton. It's a matter of preference.
this = sys.modules[__name__]

# The source HDA's are currently stored inside the pipe source code.
hda_path = os.path.join(Environment().get_project_dir(), "byu-pipeline-tools", "houdini-tools", "otls")

# We define the template HDAs definitions here, for use in the methods below
hda_definitions = {
    Department.MATERIAL: hou.hdaDefinition(hou.sopNodeTypeCategory(), "byu_material", os.path.join(hda_path, "byu_material.hda")),
    Department.MODIFY: hou.hdaDefinition(hou.sopNodeTypeCategory(), "byu_modify", os.path.join(hda_path, "byu_modify.hda")),
    Department.HAIR: hou.hdaDefinition(hou.objNodeTypeCategory(), "byu_hair", os.path.join(hda_path, "byu_hair.hda")),
    Department.CLOTH: hou.hdaDefinition(hou.objNodeTypeCategory(), "byu_cloth", os.path.join(hda_path, "byu_cloth.hda"))
}

# The order in which these nodes appear is the order they will be created in
byu_geo_departments = [Department.MODIFY, Department.MATERIAL]
byu_character_departments = [Department.HAIR, Department.CLOTH]

hda_dir = Environment().get_hda_dir()

# Update mode types
class UpdateModes:
    SMART = "smart"
    CLEAN = "clean"
    FROZEN = "frozen"

    @classmethod
    def list_modes(cls):
        return [cls.SMART, cls.CLEAN, cls.FROZEN]

    @classmethod
    def mode_from_index(cls, index):
        return [cls.SMART, cls.CLEAN, cls.FROZEN][index]

# By default, we ignore "Asset Controls", so that we can put things in there without them being promoted.
# See: inherit_parameters() method
default_ignored_folders = ["Asset Controls"]

'''
    Easily callable method, meant for tool scripts
'''
def tab_in(parent, asset_name, already_tabbed_in_node=None, excluded_departments=[]):
    body = Project().get_body(asset_name)
    if body is None or not body.is_asset():
        message_gui.error("Pipeline error: This asset either doesn't exist or isn't an asset.")
        return
    if body.get_type() == AssetType.CHARACTER:
        return byu_character(parent, asset_name, already_tabbed_in_node, excluded_departments)
    elif body.get_type() == AssetType.PROP:
        return byu_geo(parent, asset_name, already_tabbed_in_node, excluded_departments)
    elif body.get_type() == AssetType.SET:
        return byu_set(parent, asset_name, already_tabbed_in_node)
    else:
        message_gui.error("Pipeline error: this asset isn't a character, prop or set.")
        return

'''
    Easily callable method, meant for tool scripts
'''
def update_contents(node, asset_name, mode=UpdateModes.SMART):
    #super_print("{0}() line {1}:\n\tasset: {2}\n\tmode: {3}\n\tnode type name: {4}".format(method_name(), lineno(), asset_name, mode, node.type().name()))
    if node.type().name() == "byu_set":
        update_contents_set(node, asset_name, mode=mode)
    elif node.type().name() == "byu_character":
        update_contents_character(node, asset_name, mode=mode)
    elif node.type().name() == "byu_geo":
        update_contents_geo(node, asset_name, mode=mode)

'''
    This function tabs in a BYU Set and fills its contents with other BYU Geo nodes based on JSON data
'''
def byu_set(parent, set_name, already_tabbed_in_node=False, mode=UpdateModes.CLEAN):

    # Check if it's a set and that it exists
    body = Project().get_body(set_name)
    if not body.is_asset() or not body.get_type() == AssetType.SET:
        message_gui.error("Must be a set.")

    node = already_tabbed_in_node if already_tabbed_in_node else parent.createNode("byu_set")
    node.parm("set").set(set_name)
    node.parm("data").set({"set_name": set_name})

    # Update contents in the set
    update_contents_set(inside, set_name, mode)
    return node

'''
    Updates the contents of a set
'''
def update_contents_set(node, set_name, mode=UpdateModes.SMART):

    # Check if reference file exists
    set_file = os.path.join(Project().get_assets_dir(), set_name, "references.json")

    # Error checking
    try:
        with open(set_file) as f:
            set_data = json.load(f)
    except Exception as error:
        message_gui.error("No valid JSON file for " + set_name)
        return

    inside = node.node("inside")

    # Utility function to find if a node's asset and version number match an entry in the set's JSON
    def matches_reference(child, reference):

        # Grab data off the node. This data is stored as a key-value map parameter
        data = current_child.parm("data").evalAsJSONMap()

        # If it matches both the asset_name and version_number, it's a valid entry in the list
        if data["asset_name"] == reference["asset_name"] and data["version_number"] == reference["version_number"]:
            return True
        else:
            return False

    # Grab current BYU Dynamic Content Subnets that have been tabbed in
    current_children = [child for child in inside.children() if child.type().name() in ["byu_set", "byu_character", "byu_geo"]]

    # Smart updating will only destroy assets that no longer exist in the Set's JSON list
    if mode == UpdateModes.SMART:

        # Check if each child still exists in the set's JSON
        for child in current_children:
            matches = False
            for reference in set_data:
                matches = matches_reference(child, set_data)
                if matches:
                    break
            # If it doesn't, destroy it
            if not matches:
                child.destroy()

    # Clean updating will destroy all children.
    elif mode == UpdateModes.CLEAN:

        # Clear all child nodes.
        inside.deleteItems(inside.children())

    # Tab-in/update all assets in list
    for reference in set_data:

        # Tab the subnet in if it doesn't exist, otherwise update_contents
        subnet = [child for child in current_children if matches_reference(child, reference)]
        if subnet is None:
            subnet = tab_in(inside, reference["asset_name"])
        else:
            update_contents(subnet, reference["asset_name"], mode)

        # Try to not override parameters in the set
        if mode == UpdateModes.SMART:
            for key in reference:
                # Pull parm from node
                parm = subnet.parm(key)
                # If a non-default value is there, it most likely came from a user. Don't overwrite it.
                if parm.isAtDefault():
                    parm.set(reference[key])

        # Override parameters in the set
        elif mode == UpdateModes.CLEAN:
            subnet.setParms(reference)

        # Set the data
        subnet.parm("data").set({
            "asset_name": str(reference["asset_name"]),
            "version_number" : str(reference["version_number"])
        })

    inside.layoutChildren()

'''
    This function tabs in a BYU Character node and fills its contents with the appropriate character name.
    Departments is a mask because sometimes we tab this asset in when we want to work on Hair or Cloth, and don't want the old ones to be there.
'''
def byu_character(parent, asset_name, already_tabbed_in_node=None, excluded_departments=[], mode=UpdateModes.CLEAN):

    # Set up the body/elements and make sure it's a character
    body = Project().get_body(asset_name)
    if not body.is_asset() or not body.get_type() == AssetType.CHARACTER:
        message_gui.error("Must be a character.")
        return None

    # If there's an already tabbed in node, set it to that node
    node = already_tabbed_in_node if already_tabbed_in_node else parent.createNode("byu_character")
    node.setName(asset_name.title(), unique_name=True)
    node.parm("character").set(asset_name)

    # Set the asset_name data tag
    data = node.parm("data").evalAsJSONMap()
    data["asset_name"] = asset_name
    node.parm("data").set(data)

    # Set the contents to the character's nodes
    update_contents_character(node, asset_name, excluded_departments, mode)
    return node

'''
    This function sets the inner contents of a BYU Character node.
'''
def update_contents_character(node, asset_name, excluded_departments=[], mode=UpdateModes.SMART):

    ##super_print("{0}() line {1}:\n\tcharacter: {2}\n\tmode: {3}".format(method_name(), lineno(), asset_name, mode))
    # Set up the body/elements and make sure it's a character. Just do some simple error checking.
    body = Project().get_body(asset_name)
    if not body.is_asset() or body.get_type() != AssetType.CHARACTER or "byu_character" not in node.type().name():
        message_gui.error("Must be a character.")
        return None
    elements = [d for d in body.default_departments() if len(body.list_elements(d)) > 0]
    inside = node.node("inside")

    # Make sure the geo is set correctly
    geo = inside.node("geo")
    if geo is not None:
        if mode == UpdateModes.SMART:
            update_contents_geo(geo, asset_name, excluded_departments, mode)
        elif mode == UpdateModes.CLEAN:
            geo.destroy()
            geo = byu_geo(inside, asset_name, excluded_departments=excluded_departments, character=True)
    else:
        geo = byu_geo(inside, asset_name, excluded_departments=excluded_departments, character=True)

    # Tab in each content HDA based on department
    for department in this.byu_character_departments:
        # If the department is not excluded, tab-in/update the content node like normal
        if department not in excluded_departments:

            update_content_node(node, inside, asset_name, department, mode)
        # If the department is excluded, we should delete it.
        elif mode == UpdateModes.CLEAN:

            destroy_if_there(inside, department)

    inside.layoutChildren()
    ##super_print("{0}() returned {1}".format(method_name(), node))
    return node

'''
    This function tabs in a BYU Geo node and fills its contents according to the appropriate asset name.
'''
def byu_geo(parent, asset_name, already_tabbed_in_node=None, excluded_departments=[], character=False, mode=UpdateModes.CLEAN):
    # Set up the body/elements and check if it's an asset.
    body = Project().get_body(asset_name)
    if not body.is_asset():
        message_gui.error("Must be an asset.")
        return None

    # Set up the nodes, name geo
    node = already_tabbed_in_node if already_tabbed_in_node else parent.createNode("byu_geo")
    if character:
        node.setName("geo")
    else:
        node.setName(asset_name.title(), unique_name=True)

    # Set the asset_name data tag
    data = node.parm("data").evalAsJSONMap()
    data["asset_name"] = asset_name
    node.parm("data").set(data)

    # Set the contents to the nodes that belong to the asset
    update_contents_geo(node, asset_name, excluded_departments, mode)
    return node

'''
    This function sets the dynamic inner contents of a BYU Geo node.
'''
def update_contents_geo(node, asset_name, excluded_departments=[], mode=UpdateModes.SMART):

    # Set up the body/elements and make sure it's a character. Just do some simple error checking.
    body = Project().get_body(asset_name)
    if body is None:
        message_gui.error("Asset doesn't exist.")
        return None
    if not body.is_asset() or body.get_type() == AssetType.SET or "byu_geo" not in node.type().name():
        message_gui.error("Must be a prop or character.")
        return None

    # Get interior nodes
    importnode = node.node("import")
    inside = node.node("inside")

    # Set the asset_name and reload
    if node.parm("asset_name").evalAsString() != asset_name:
        node.parm("asset_name").set(asset_name)
    importnode.parm("reload").pressButton()

    # Tab in each content HDA based on department
    for department in this.byu_geo_departments:
        # If the department is not excluded, tab-in/update the content node like normal
        if department not in excluded_departments:
            update_content_node(node, inside, asset_name, department, mode, inherit_parameters = department == Department.MODIFY)
        # If the department is excluded, we should delete it.
        elif mode == UpdateModes.CLEAN:
            destroy_if_there(inside, department)

    inside.layoutChildren()
    return node

'''
    Creates new content HDAs
'''
def create_hda(asset_name, department):

    # Check if this body is an asset. If not, return error.
    body = Project().get_body(asset_name)
    if not body.is_asset():
        message_gui.error("Must be an asset of type PROP or CHARACTER.")
        return

    # Check if it is a set.
    if body.get_type() == AssetType.SET:
        message_gui.error("Asset must be a PROP or CHARACTER.")
        return

    # Check if the user is trying to create a Hair or Cloth asset for a Prop on accident.
    if body.get_type() == AssetType.PROP and (department == Department.HAIR or department == Department.CLOTH):
        message_gui.error("Hair and cloth should only be made for characters.")
        return

    # Create element if does not exist.
    element = body.get_element(department, name=Element.DEFAULT_NAME, force_create=True)

    # TODO: Get rid of this ugly hotfix
    # !!! HOTFIX !!!
    # Material was previously used as an AssetElement, but now is being treated like an HDAElement.
    # This will convert it's file extension to .hdanc. (Before, it's extension was "").
    element._datadict[Element.APP_EXT] = element.create_new_dict(Element.DEFAULT_NAME, department, asset_name)[Element.APP_EXT]
    element._update_pipeline_file()
    # !!! END HOTFIX !!!

    # Check out the department.
    username = Project().get_current_username()
    checkout_file = element.checkout(username)

    # Tab in the parent asset that will hold this checked out HDA
    node = tab_in(hou.node("/obj"), asset_name, excluded_departments=[department])

    # If it's a character and it's not a hair or cloth asset, we need to reach one level deeper.
    if body.get_type() == AssetType.CHARACTER and department not in this.byu_character_departments:
        inside = node.node("inside/geo/inside")
    else:
        inside = node.node("inside")

    # CREATE NEW HDA DEFINITION
    operator_name = element.get_parent() + "_" + element.get_department()
    operator_label = (asset_name.replace("_", " ") + " " + element.get_department()).title()
    this.hda_definitions[department].copyToHDAFile(checkout_file, operator_name, operator_label)
    hda_type = hou.objNodeTypeCategory() if department in this.byu_character_departments else hou.sopNodeTypeCategory()
    hou.hda.installFile(checkout_file)
    hda_definition = hou.hdaDefinition(hda_type, operator_name, checkout_file)
    hda_definition.setPreferred(True)

    # Tab an instance of this new HDA into the asset you are working on
    try:
        hda_instance = inside.createNode(asset_name + "_" + department)
    except Exception as e:
        message_gui.error("HDA Creation Error. " + asset_name + "_" + department + " must not exist.")
    hda_instance.setName(department)
    tab_into_correct_place(inside, hda_instance, department)
    hda_instance.allowEditingOfContents()
    hda_instance.setSelected(True, clear_all_selected=True)

'''
    Updates a content node.
'''
def update_content_node(parent, inside, asset_name, department, mode=UpdateModes.SMART, inherit_parameters=False, ignore_folders=this.default_ignored_folders):

    #super_print("{0}() line {1}:\n\tasset_name: {2}\n\tdepartment: {3}\n\tmode: {4}".format(method_name(), lineno(), asset_name, department, mode))
    # See if there's a content node with this department name already tabbed in.
    content_node = inside.node(department)
    #super_print("\tline {0}: content_node = {1}".format(lineno() - 1, content_node))

    # If the content node exists.
    if content_node is not None:
        # Check if the node is currently being edited.
        if not content_node.matchesCurrentDefinition():
            # Clean is a destructive mode that will destroy it.
            if mode == UpdateModes.CLEAN:
                content_node.destroy()
            # Else, don't touch the node if it's being edited.
            else:
                return content_node
        # Else, we need to destroy the old node. This happens in SMART mode
        else:
            try:
                content_node.destroy()
            except Exception as e:
                print(e)

    is_published = published_definition(asset_name, department)
    ##super_print("{0}() returned from published_definition() as {1}".format(method_name(), is_published))
    # This line checks to see if there's a published HDA with that name.
    if is_published:
        # Only create it if it's in the pipe.
        ##super_print("{0}() line {1}:\n\tlocals: {2}".format(method_name(), lineno(), str(locals())))
        content_node = inside.createNode(asset_name + "_" + department)
        if content_node:
            tab_into_correct_place(inside, content_node, department)
            content_node.setName(department)
            # Some nodes will promote their parameters to the top level
            if inherit_parameters:
                inherit_parameters_from_node(parent, content_node, mode, ignore_folders)


    ##super_print("{0}() returned {1}".format(method_name(), content_node))
    return content_node

'''
    Destroys unwanted content nodes if they remain in a network
'''
def destroy_if_there(inside, department):
    node = inside.node(department)
    if node is not None:
        node.destroy()

'''
    Check if a definition is the published definition or not
'''
def published_definition(asset_name, department):

    ##super_print("{0}() line {1}:\n\tasset_name: {2}\n\tdepartment: {3}".format(method_name(), lineno(), asset_name, department))
    # Set the node type correctly
    node_type = hou.objNodeTypeCategory() if department in this.byu_character_departments else hou.sopNodeTypeCategory()
    #super_print("{0}() line {1}:\n\tlocals: {2}".format(method_name(), lineno(), str(locals())))

    # TODO: Get rid of this hotfix
    # !!! HOTFIX !!!
    # We have to append _main to the HDAs, because that's how they publish
    production_hda_filename = asset_name + "_" + department + "_" + Element.DEFAULT_NAME + ".hdanc"
    # !!! END HOTFIX !!!
    ##super_print("{0}() line {1}:\n\tlocals: {2}".format(method_name(), lineno(), str(locals())))

    # Get the HDA path, if doesn't exist return false
    production_hda_path = os.path.join(this.hda_dir, production_hda_filename)

    try:
        if not os.path.islink(os.path.join(Environment().get_project_dir(), "production", "hda", production_hda_filename)):
            #super_print("{0}() line {1}:\n\tlocals: {2}".format(method_name(), lineno(), str(locals())))
            return False
    except Exception as e:
        print (e)
        ##super_print("{0}() line {1}:\n\tlocals: {2}\n\texception: {3}".format(method_name(), lineno(), str(locals()), str(e)))

    # This doesn't work unless you follow the symlink_path, I don't know why it works elsewhere
    resolved_symlink_path = os.readlink(production_hda_path)
    #super_print("{0}() line {1}:\n\tlocals: {2}".format(method_name(), lineno(), str(locals())))

    # Install the file and get definitions from it
    hou.hda.installFile(resolved_symlink_path)
    #super_print("{0}() line {1}:\n\tlocals: {2}".format(method_name(), lineno(), str(locals())))
    definitions = hou.hda.definitionsInFile(resolved_symlink_path)
    #super_print("{0}() line {1}:\n\tlocals: {2}".format(method_name(), lineno(), str(locals())))

    # Get the HDA definition from production, make it preferred if exists
    hda_definition = next(definition for definition in definitions if definition.nodeTypeName() == asset_name + "_" + department)
    #super_print("{0}() line {1}:\n\tlocals: {2}".format(method_name(), lineno(), str(locals())))
    if hda_definition is not None:
        hda_definition.setPreferred(True)
        ##super_print("{0}() returned {1}".format(method_name(), True))
        return True
    else:
        #super_print("decided not to tab in " + str(node_type) + " type node named " + asset_name + "_" + department + " from " + resolved_symlink_path)
        ##super_print("{0}() returned {1}".format(method_name(), False))
        return False

'''
    Promote parameters from an inner node up to an outer node.
'''
def inherit_parameters_from_node(upper_node, inner_node, mode=UpdateModes.SMART, ignore_folders=[]):

    # Get the lists of parms
    upper_spare_parms = inner_node.spareParms()
    inner_parms = inner_node.parms()
    inner_parm_names = [parm.name() for parm in inner_parms]

    # Only remove the spare parms that are no longer on the inner_node
    if mode == UpdateModes.SMART:
        for upper_spare_parm in upper_spare_parms:
            if upper_parm.name() not in inner_parm_names:
                upper_node.removeSpareParmTuple(inner_parm.parmTemplate())

    # Clean all spare parms
    elif mode == UpdateModes.CLEAN:
        upper_node.removeSpareParms()

    # Else, don't do anything
    elif mode == UpdateModes.FROZEN:
        return

    for inner_parm in inner_parms:

        # This isn't very elegant, but I need to check if any containing folders contain any substrings from ignore_folders
        in_containing_folder = False
        for folder in ignore_folders:
            for containingFolder in inner_parm.containingFolders():
                if folder in containingFolder:
                    in_containing_folder = True
                    break
            if in_containing_folder:
                break
        if in_containing_folder:
            continue
        # That's the end of the non-elegant solution

        # If not in the ignored folders, then either set the value or promote it
        upper_parm = upper_node.parm(inner_parm.name())
        if upper_parm is not None:
            upper_parm.set(inner_parm.eval())
        else:
            upper_node.addSpareParmTuple(inner_parm.parmTemplate(), inner_parm.containingFolders(), True)

'''
    Helper function for create_hda()
'''
def tab_into_correct_place(inside, node, department):

    # If the node belongs inside a BYU Character, do the following
    if department in this.byu_character_departments:

        # Hair and Cloth assets should be connected to geo. If it doesn't exist, throw an error.
        geo = inside.node("geo")
        if geo is None:
            message_gui.error("There should be a geo network. Something went wrong.")
            return

        # Attach the Hair or Cloth asset to the geo network.
        node.setInput(0, geo)

    # If the node belongs inside a BYU Geo, do the following
    else:

        # Shot_modeling and geo are our way of knowing where to insert nodes. If either of them is null, throw an error.
        geo = inside.node("geo")
        shot_modeling = inside.node("shot_modeling")
        if shot_modeling is None or geo is None:
            message_gui.error("There should be a shot_modeling and geo network. Something went wrong.")
            return None

        # If we're inserting a modify node, do the following
        if department == Department.MODIFY:

            # If there is a material node, put the modify node in between material and geo.
            material = inside.node("material")
            if material is not None:
                node.setInput(0, geo)
                material.setInput(0, node)

            # Else, stick it between geo and shot_modeling.
            else:
                node.setInput(0, geo)
                shot_modeling.setInput(0, node)

        # If we're inserting a material node, do the following
        elif department == Department.MATERIAL:

            # If there is a modify node, put the material node in between modify and shot_modeling.
            modify = inside.node("modify")
            if modify is not None:
                node.setInput(0, modify)
                shot_modeling.setInput(0, node)

            # Else, stick it between geo and shot_modeling.
            else:
                node.setInput(0, geo)
                shot_modeling.setInput(0, node)

    inside.layoutChildren()
    return node
