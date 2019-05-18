import maya.cmds as mc
import maya.mel as mel
import pymel.core as pm
from byuam import Project, Department, AssetType
import json, os, traceback

def exportProp(body):
    project = Project()
    element = body.get_element(Department.MODEL)
    filePath = os.path.join(project.get_assets_dir(), element.get_cache_dir())
    assemblies = pm.ls(assemblies=True)
    pm.select(pm.listCameras(), replace=True)
    cameras = pm.selected()
    pm.select([])
    non_cameras = [assembly for assembly in assemblies if assembly not in cameras]
    if len(non_cameras) > 0:
        exportPropJSON(filePath, non_cameras[0], isReference=False, name=body.get_name())
    else:
        print "No non-camera assets found. Most likely this is a camera asset."

def exportPropJSON(filePath, rootNode, isReference=True, name="", version_number=None):
    if isReference:
        name, version_number = getReferenceName(rootNode)
    body = Project().get_body(name)
    if not body or not body.is_asset() or body.get_type() != AssetType.PROP:
        print "The asset %s does not exist as a prop, skipping.".format(name)
        return None

    # Check if verNum is nothing - if so, we need to make it be an int 0
    if not version_number:
        version_number = 0

    def strip_reference(input):
        i = input.rfind(":")
        if i == -1:
            return input
        return input[i + 1:]

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

    verts = firstMesh.vtx
    vertpos1 = verts[0].getPosition(space='world')
    vertpos2 = verts[1].getPosition(space='world')
    vertpos3 = verts[2].getPosition(space='world')

    # Put all relevant data into dictionary object
    json_data = {"asset_name": name,
                 "version_number": version_number,
                 "path" : path,
                 "a" : [vertpos1.x, vertpos1.y, vertpos1.z],
                 "b" : [vertpos2.x, vertpos2.y, vertpos2.z],
                 "c" : [vertpos3.x, vertpos3.y, vertpos3.z] }

    # Write JSON to fill
    jsonRef = json.dumps(json_data)
    wholePath = os.path.join(filePath, os.path.join(filePath, name + "_" + str(version_number) + ".json"))
    outfile = open(wholePath, "w")  # *** THIS IS THE NAME OF THE OUTPUT FILE ***
    outfile.write(jsonRef)
    outfile.close()

    return {"asset_name" : json_data["asset_name"], "version_number" :  json_data["version_number"]}

def getReferenceName(ref):
    # When we get the file name we need to make sure that we also get the reference number. This will allow us to have multiple alembics from a duplicated reference.
    refPath = pm.referenceQuery(unicode(ref), filename=True)
    print("ref= " + ref)
    print("refpath= " + refPath)
    #refName = str(ref).split(':')[1]
    refName = refPathToRefName(refPath)
    print("refName= " + refName)

    start = refPath.find('{')
    end = refPath.find('}')
    if start == -1 or end == -1:
        vernum = ''
    else:
        vernum = refPath[start+1:end]
    return refName, vernum
