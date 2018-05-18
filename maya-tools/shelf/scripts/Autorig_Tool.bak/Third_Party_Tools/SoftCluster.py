"""
Script by Jeroen Hoolmans (jhoolmans) found on GitHub
"""


import maya.cmds as mc
import maya.OpenMaya as om

def softSelection():
    selection = om.MSelectionList()
    softSelection = om.MRichSelection()
    om.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)

    dagPath = om.MDagPath()
    component = om.MObject()

    iter = om.MItSelectionList( selection,om.MFn.kMeshVertComponent )
    elements = []
    while not iter.isDone():
        iter.getDagPath( dagPath, component )
        dagPath.pop()
        node = dagPath.fullPathName()
        fnComp = om.MFnSingleIndexedComponent(component)

        for i in range(fnComp.elementCount()):
            elements.append([node, fnComp.element(i), fnComp.weight(i).influence()] )
        iter.next()
    return elements


def createSoftCluster(name=''):
    
    """
    @param name: str, base name of cluster
    """

    softElementData = softSelection()
    selection = ["%s.vtx[%d]" % (el[0], el[1])for el in softElementData ]

    mc.select(selection, r=True)
    cluster = mc.cluster(relative=True, name=name)

    for i in range(len(softElementData)):
        mc.percent(cluster[0], selection[i], v=softElementData[i][2])
    mc.select(cluster[1], r=True)
