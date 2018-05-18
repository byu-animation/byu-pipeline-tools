"""
transform @ utilities

functions to manipulate and create transforms
"""

import maya.cmds as mc

from . import naming

def make_offset_group( object, prefix = '' ):
    
    """
    make offset group for given object
    
    @param object: transform object to receive offset group
    @param prefix: str, prefix to name offset group
    @return: str, name of new offset group
    """
    
        
    if not prefix:
        prefix = naming.remove_suffix( object )
        
    offset_GRP = mc.group( name = prefix + '_os_grp_01', empty = True, world=True)
    
    object_parents = mc.listRelatives(object, parent=True)
    
    if object_parents:
        mc.parent( offset_GRP, object_parents[0] )
            
    #match offset group's transforms to object transforms
    mc.delete( mc.parentConstraint( object, offset_GRP ))
    mc.delete( mc.scaleConstraint( object, offset_GRP ))
    
    # parent object under offset group
    mc.parent( object, offset_GRP, absolute=False )
    
    # compensate for "eccentric" default Maya joint parenting behavior 
    mc.select(object)
    current_object=mc.ls(selection=True)
    object_type=mc.objectType(current_object)
    if object_type=='joint':
        mc.setAttr(current_object[0] + '.jointOrientX', 0.0)
        mc.setAttr(current_object[0] + '.jointOrientY', 0.0)
        mc.setAttr(current_object[0] + '.jointOrientZ', 0.0)
        mc.setAttr(current_object[0] + '.rotateX', 0.0)
        mc.setAttr(current_object[0] + '.rotateY', 0.0)
        mc.setAttr(current_object[0] + '.rotateZ', 0.0)

    
    return offset_GRP
    
    
def freeze_locked_transforms( object ):
    
    """
    unlock channel box attrs, freeze transforms, and relock attrs for given object
    
    @param object: transform object to be frozen
    """
    
    ########################needs to be made iterative to take care of children or freeze transforms won't work######################
    
    #create list to store locked attributes
    locked_attributes=[]
    
    for attribute in ['.translate', '.scale', '.rotate', '.translateX', '.translateY', '.translateZ', '.rotateX', '.rotateY', '.rotateZ', '.scaleX', '.scaleY', '.scaleZ']: 
        
        #see if attribute is locked or not
        locked=(mc.getAttr( object + attribute, lock=True ))
        print(object+attribute)
        print(locked)
        #if attribute is locked, store it in a list and unlock it
        if locked==True:
            print('ran')
            mc.setAttr(object + attribute, lock=False, keyable=True)
            locked_attributes.append(attribute)
            print(locked_attributes)
    #freeze object tranforms
    mc.makeIdentity(object, apply=True, translate=True, rotate=True, scale=True)
    
    #relock previously locked attributes
    for locked_attribute in locked_attributes:
        mc.setAttr(object + locked_attribute, lock=True)



















    
    
    
    
    