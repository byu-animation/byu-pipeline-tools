# Interfacing with maya through pymel commands
import pymel.core as pm
import os
from PySide2 import QtWidgets
from byuam import *

def maya_main_window():
    for obj in QtWidgets.qApp.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')

def get_scene_file():
    filename = pm.system.sceneName()
    if not filename:
        filename = os.environ['HOME']
        filename = os.path.join(filename, 'untitled.mb')
        return filename, True
    else:
        return filename, False

def save_scene_file():
    filename, untitled = get_scene_file()
    if untitled:
        pm.system.renameFile(filename)
    return pm.system.saveFile()

def clear_construction_history():
    pm.delete(constructionHistory=True, all=True)

def freeze_transformations():
    failed = []
    objects = pm.ls(transforms=True)
    for scene_object in objects:
        try:
            pm.makeIdentity(scene_object, apply=True)
        except:
            failed.append(scene_object)
    return failed

def convert_to_education():
    pm.FileInfo()['license'] = 'education'

def get_top_level_nodes():
    assemblies = pm.ls(assemblies=True)
    pm.select(pm.listCameras(), replace=True)
    cameras = pm.selected()
    pm.select([])
    return [assembly for assembly in assemblies if assembly not in cameras]

def group_top_level():
    top_level_nodes = get_top_level_nodes()
    for top_level_node in top_level_nodes:
        # If the top level has a mesh, group it.
        if top_level_node.getShape() is not None:
            pm.group(top_level_nodes)
    # If the top level has more than one node, group it.
    if len(top_level_nodes) > 1:
        pm.group(top_level_nodes)

def delete_image_planes():
    objects = pm.ls()
    for scene_object in objects:
        if isinstance(scene_object, pm.nodetypes.ImagePlane):
            pm.delete(scene_object)

def get_loaded_references():
    references = pm.ls(references=True, transforms=True)
    loaded=[]
    for ref in references:
        print "Checking status of " + ref
        try:
            if ref.isLoaded():
                loaded.append(ref)
        except:
            print "Warning: " + ref + " was not associated with a reference file"
    return loaded

def extract_reference_data(ref):
    refPath = pm.referenceQuery(unicode(ref), filename=True)
    refName = refPathToRefName(refPath)
    start = refPath.find('{')
    end = refPath.find('}')
    if start == -1 or end == -1:
        vernum = ''
    else:
        vernum = refPath[start+1:end]
    return refName, vernum

def strip_reference(input):
    i = input.rfind(":")
    if i == -1:
        return input
    return input[i + 1:]

def find_first_mesh(rootNode):
    firstMesh = None
    path = ""
    stack = []
    stack.append(rootNode)
    while len(stack) > 0 and firstMesh is None:
        curr = stack.pop()
        path = path + "/" + strip_reference(curr.name())
        for child in curr.getChildren():
            if isinstance(child, pm.nodetypes.Shape):
                firstMesh = child
                path = path + "/" + strip_reference(child.name())
                break
            elif not isinstance(child, pm.nodetypes.Transform):
                continue
            if child.getShape() is not None:
                firstMesh = child.getShape()
                path = path + "/" + strip_reference(child.name()) + "/" + strip_reference(child.getShape().name())
                break
        for child in curr.getChildren():
            stack.append(child)

def get_anchor_points(mesh):
    verts = mesh.vtx
    vertpos1 = verts[0].getPosition(space='world')
    vertpos2 = verts[1].getPosition(space='world')
    vertpos3 = verts[2].getPosition(space='world')
    return {
        "a" : vertpos1,
        "b" : vertpos2,
        "c" : vertpos3
    }

def get_body_from_reference(ref):
    return Project().get_body(extract_reference_data(ref)[0])

def get_root_node_from_reference(ref):
    refPath = pm.referenceQuery(unicode(ref), filename=True)
    refNodes = pm.referenceQuery(unicode(refPath), nodes=True )
    rootNode = pm.ls(refNodes[0])[0]
    return rootNode

'''
    Tagging nodes with flags
'''

def tag_node_with_flag(node, flag):
    if not node_is_tagged_with_flag(node, flag):
        pm.cmds.lockNode(str(node), l=False)
        node.addAttr(flag, dv=True, at=bool, h=False, k=True)

def untag_node_with_flag(node, flag):
    if node_is_tagged_with_flag(node, flag):
        node.deleteAttr(flag)

def node_is_tagged_with_flag(node, flag):
    if node.hasAttr(flag):
        return True

def children_tagged_with_flag(node, flag):
    for child in node.listRelatives(allDescendants=True):
        if node_is_tagged_with_flag(child, flag):
            return True
    return False

def get_first_child_with_flag(node, flag):
    stack = []
    stack.append(node)
    while len(stack) > 0:
        curr = stack.pop()
        for child in curr.getChildren():
            if node_is_tagged_with_flag(child, flag):
                return child
        for child in curr.getChildren():
            stack.append(child)

class ExportFlags:
    EXPORT_TARGET = "BYU_Export_Target_Flag"
    ANIMATED = "BYU_Animated_Flag"


def has_parent_set(rootNode):
    project = Project()
    parent_is_set = False
    parent_node = rootNode.getParent()
    while parent_node is not None:
        asset_name, _ = getReferenceName(parent_node)
        parent_body = project.get_body(asset_name)
        if parent_body is not None and parent_body.is_asset() and parent_body.get_type() == AssetType.SET:
            parent_is_set = True
            break
        parent_node = parent_node.parent_node()
    if parent_is_set:
        return True
    return False

def get_reference_as_string(ref):
    name, version_number = extract_reference_data(ref)
    return name + "_" + str(version_number)

def get_references_as_list():
    return [reference_as_string(ref) for ref in get_loaded_references()]

def get_references_as_node_dict():
    result = {}
    for ref in get_loaded_references():
        result[reference_as_string(ref)] = get_root_node_from_reference(ref)
