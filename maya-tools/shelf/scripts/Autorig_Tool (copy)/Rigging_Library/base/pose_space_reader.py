"""
Module for making pose space readers.
"""

import maya.cmds as mc

"""
Class for building pose space reader
"""
class PoseSpaceReader():

    def __init__(
               self,
               prefix = 'test',
               scale = 1.0,
               base_object = '',
               tracker_object = '',
               base_name = 'test',
               tracker_name = 'test',
               target_names = ['test'],
               parent = '',
              ):


        """
        @param prefix: str, base for PSR name
        @param scale: float, scale value for size of control shapes
        @param base_object: str, name of object to which base will be constrained
        @param tracker_object: str, name of object to which tracker will be constrained
        @param base_name: str, name of object which determines origin of pose reader
        @param tracker_name: str, name of tracker whose proximity to the targets the PSR will calculate
        @param target_names: list of strings, names of objects which will serve as pose targets in reference to pose reader base
        @param parent: str, object to be parent of whole PSR

        @return: None
        """

        # Create and position locators
        mc.spaceLocator(name=prefix + '_' + base_name + '_PSR_loc_01')
        mc.pointConstraint(base_object, prefix + '_' + base_name + '_PSR_loc_01')
        mc.spaceLocator(name=prefix + '_' + tracker_name + '_PSR_loc_01')
        mc.pointConstraint(tracker_object, prefix + '_' + tracker_name + '_PSR_loc_01')
        
        # create decompose matrix nodes and connect to locators to obtain worldspace coordinates
        mc.shadingNode('decomposeMatrix', asUtility=True, name=prefix + '_' + base_name + '_DM_01')
        mc.connectAttr(prefix + '_' + base_name + '_PSR_loc_01.worldMatrix', prefix + '_' + base_name + '_DM_01.inputMatrix')
        mc.shadingNode('decomposeMatrix', asUtility=True, name=prefix + '_' + tracker_name + '_DM_01')
        mc.connectAttr(prefix + '_' + tracker_name + '_PSR_loc_01.worldMatrix', prefix + '_' + tracker_name + '_DM_01.inputMatrix')
        
        # create PMA node to serve as tracker vector
        mc.shadingNode('plusMinusAverage', asUtility=True, name=prefix + '_' + base_name + '_tracker_vector_PMA_01')
        mc.setAttr( prefix + '_' + base_name + '_tracker_vector_PMA_01.operation', 2)
        
        # connect DM nodes to make tracker vector
        mc.connectAttr(prefix + '_' + tracker_name + '_DM_01.outputTranslate', prefix + '_' + base_name + '_tracker_vector_PMA_01.input3D[0]')
        mc.connectAttr(prefix + '_' + base_name + '_DM_01.outputTranslate', prefix + '_' + base_name + '_tracker_vector_PMA_01.input3D[1]')
        
        
        # make targets
        for target_name in target_names:
            # make target
            mc.spaceLocator(name=prefix + '_' + base_name + '_' + target_name + '_PSR_loc_01')
            mc.delete(mc.pointConstraint(base_object, prefix + '_' + base_name + '_' + target_name + '_PSR_loc_01'))
            mc.move(0.0, scale*(target_names.index(target_name)+1), 0.0, prefix + '_' + base_name + '_' + target_name + '_PSR_loc_01', relative=True)
            
            # create custom attributes to store posereader angles
            mc.addAttr(prefix + '_' + base_name + '_PSR_loc_01', shortName = target_name + '_angle', longName = target_name + '_Angle', defaultValue = 45.0, minValue = 0.0, maxValue = 360.0, keyable=True )
            
            # create decompose matrix node and connect to locator to obtain its worldspace coordinates
            mc.shadingNode('decomposeMatrix', asUtility=True, name=prefix + '_' + base_name + '_' + target_name + '_DM_01')
            mc.connectAttr(prefix + '_' + base_name + '_' + target_name + '_PSR_loc_01.worldMatrix', prefix + '_' + base_name + '_' + target_name + '_DM_01.inputMatrix')
            
            # create angle between node 
            mc.shadingNode('angleBetween', asUtility=True, name=prefix + '_' + base_name + '_' + target_name + '_ANB_01')
            
            # create MD, PMA, and COND nodes
            mc.shadingNode('plusMinusAverage', asUtility=True,  name=prefix + '_' + base_name + '_' + target_name + '_target_vector_PMA_01')
            mc.setAttr( prefix + '_' + base_name + '_' + target_name + '_target_vector_PMA_01.operation', 2)
            mc.shadingNode('multiplyDivide', asUtility=True, name=prefix + '_' + base_name + '_' + target_name + '_PSR_divide_by_angle_attribute_MD_01')
            mc.setAttr( prefix + '_' + base_name + '_' + target_name + '_PSR_divide_by_angle_attribute_MD_01.operation', 2)
            mc.shadingNode('plusMinusAverage', asUtility=True,  name=prefix + '_' + base_name + '_' + target_name + '_PSR_invert_PMA_01')
            mc.setAttr( prefix + '_' + base_name + '_' + target_name + '_PSR_invert_PMA_01.operation', 2)
            mc.setAttr( prefix + '_' + base_name + '_' + target_name + '_PSR_invert_PMA_01.input3D[0].input3Dx', 1.0)
            mc.shadingNode('condition', asUtility=True, name= prefix + '_' + base_name + '_' + target_name + '_PSR_COND_01')
            mc.setAttr( prefix + '_' + base_name + '_' + target_name + '_PSR_COND_01.operation', 2)
            mc.setAttr( prefix + '_' + base_name + '_' + target_name + '_PSR_COND_01.secondTerm', 0.0)
            mc.setAttr( prefix + '_' + base_name + '_' + target_name + '_PSR_COND_01.colorIfFalse.colorIfFalseR', 0.0)
            
            # connect DM nodes to vector
            mc.connectAttr( prefix + '_' + base_name + '_' + target_name + '_DM_01.outputTranslate', prefix + '_' + base_name + '_' + target_name + '_target_vector_PMA_01.input3D[0]')
            mc.connectAttr( prefix + '_' + base_name + '_DM_01.outputTranslate', prefix + '_' + base_name + '_' + target_name + '_target_vector_PMA_01.input3D[1]')

            # connect vectors to angle between nodes, divide by angle attribute, invert, and then pipe output into condition node
            mc.connectAttr( prefix + '_' + base_name + '_' + target_name + '_target_vector_PMA_01.output3D', prefix + '_' + base_name + '_' + target_name + '_ANB_01.vector1')
            mc.connectAttr( prefix + '_' + base_name + '_tracker_vector_PMA_01.output3D', prefix + '_' + base_name + '_' + target_name + '_ANB_01.vector2')
            mc.connectAttr( prefix + '_' + base_name + '_' + target_name + '_ANB_01.angle', prefix + '_' + base_name + '_' + target_name + '_PSR_divide_by_angle_attribute_MD_01.input1X')
            mc.connectAttr( prefix + '_' + base_name + '_PSR_loc_01.' + target_name + '_angle', prefix + '_' + base_name + '_' + target_name + '_PSR_divide_by_angle_attribute_MD_01.input2X')
            mc.connectAttr( prefix + '_' + base_name + '_' + target_name + '_PSR_divide_by_angle_attribute_MD_01.outputX', prefix + '_' + base_name + '_' + target_name + '_PSR_invert_PMA_01.input3D[1].input3Dx')
            mc.connectAttr( prefix + '_' + base_name + '_' + target_name + '_PSR_invert_PMA_01.output3Dx', prefix + '_' + base_name + '_' + target_name + '_PSR_COND_01.firstTerm')
            mc.connectAttr( prefix + '_' + base_name + '_' + target_name + '_PSR_invert_PMA_01.output3Dx', prefix + '_' + base_name + '_' + target_name + '_PSR_COND_01.colorIfTrue.colorIfTrueR')
            
        # cleanup
        mc.group( prefix + '_' + base_name + '_PSR_loc_01',  name=prefix + '_' + base_name + '_PSR_GRP_01')
        mc.parent( prefix + '_' + tracker_name + '_PSR_loc_01', prefix + '_' + base_name + '_PSR_GRP_01')
        for target_name in target_names:
            mc.parent( prefix + '_' + base_name + '_' + target_name + '_PSR_loc_01', prefix + '_' + base_name + '_PSR_GRP_01')
        if parent != '':
            mc.parent( prefix + '_' + base_name + '_PSR_01', parent)
        
        # add public members
        self.C = prefix + '_' + base_name + '_PSR_GRP_01'


        
                
                
                
                
                
                
                
                
                
                
                
