"""
joint utilities @ utilities
"""


import maya.cmds as mc

def list_hierarchy( top_joint, with_end_joints = True ):
    
    """
    list joint hierarchy starting with top Joint
    
    @param top_joint: str, joint to get listed with its joint hierarchy
    @param with_end_joints: boolean, list hierarchy with end joints included
    @return list( str ), listed joints starting with top joint
    """
    
    listed_joints = mc.listRelatives( top_joint, type = 'joint', allDescendents = True)
    listed_joints.append( top_joint )
    listed_joints.reverse()
    
    complete_joints = listed_joints[:]
    
    if not with_end_joints:
        complete_joints = [ j for j in listed_joints if mc.listRelatives( j, children=True, type = 'joint')]
        
    return complete_joints