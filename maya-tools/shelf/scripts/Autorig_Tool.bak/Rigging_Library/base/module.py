"""
Module for making rig top structure and rig module.
"""

import maya.cmds as mc

scene_object_type = 'rig'

from . import control



"""
Class for building rig base
"""
class Base():
    
    def __init__(
                 self,
                 character_name = 'new', 
                 scale = 1.0              
                 ):
        
        """
        @param character_name: str, character name
        @scale: float, general scale of the rig
        @return: None
        """
        
        self.top_GRP = mc.group( name= character_name + '_GRP_01', empty = True )
        self.rig_GRP = mc.group( name= character_name + '_rig_GRP_01', empty = True, parent=self.top_GRP )
        self.geo_GRP = mc.group( name= character_name + '_geo_GRP_01', empty = True, parent=self.top_GRP )
        self.proxy_GRP = mc.group( name= character_name + '_PROXY_GRP_01', empty = True, parent=self.top_GRP )
        self.controls_GRP = mc.group( name= character_name + '_controls_GRP_01', empty = True, parent=self.rig_GRP )  
        self.skeleton_GRP = mc.group( name= character_name + '_skeleton_GRP_01', empty = True, parent=self.rig_GRP )  
        self.modules_GRP = mc.group( name= character_name + '_modules_GRP_01', empty = True, parent=self.rig_GRP )  
        self.extras_GRP = mc.group( name= character_name + '_extras_GRP_01', empty = True, parent=self.rig_GRP )      
        self.no_transform_GRP = mc.group( name= character_name + '_no_transform_GRP_01', empty = True, parent=self.rig_GRP )       
 
        mc.setAttr( self.extras_GRP + '.inheritsTransform', False, lock=True) 
        
        character_name_attribute = 'character_name'
        scene_object_type_attribute = 'scene_object_type'
        
        for attribute in [ character_name_attribute, scene_object_type_attribute]:
            mc.addAttr( self.top_GRP, longName=attribute, dataType='string')
            
        mc.setAttr( self.top_GRP + '.' + character_name_attribute, character_name, type = 'string', lock=True)
        mc.setAttr( self.top_GRP + '.' + scene_object_type_attribute, scene_object_type, type = 'string', lock=True)
        
        
  
        # add primary global control (for scaling)
        primary_global_control = control.Control(
                                                prefix = character_name + '_primary_global',
                                                scale = scale * .2,
                                                parent = self.controls_GRP,
                                                locked_channels = ['visibility']
                                                )
        
        # add secondary global control
        secondary_global_control = control.Control(
                                                  prefix = character_name + '_secondary_global',
                                                  scale = scale * .18,
                                                  parent = primary_global_control.C,
                                                  locked_channels = ['visibility', 'scale']
                                                  )
               
        self._flatten_global_control_shape( primary_global_control.C )
        self._flatten_global_control_shape( secondary_global_control.C )
        
        # rename offset group to become new secret rig scale node
        mc.rename(primary_global_control.Off, character_name + '_secret_scale_os_grp_01')           

        # bind scaling of primary global control to scaleX and hide scaleY and scaleZ
        for axis in ['y', 'z']:
            mc.connectAttr( primary_global_control.C + '.sx', primary_global_control.C + '.s' + axis)
            mc.setAttr(primary_global_control.C + '.s' + axis, keyable=False)
            
        
        # parent and scale constrain skeleton group, extras group, and modules group to globals
        mc.parentConstraint(secondary_global_control.C, self.skeleton_GRP)
        mc.scaleConstraint(secondary_global_control.C, self.skeleton_GRP)
        mc.parentConstraint(secondary_global_control.C, self.extras_GRP)
        mc.scaleConstraint(secondary_global_control.C, self.extras_GRP)
        mc.parentConstraint(secondary_global_control.C, self.modules_GRP)
        mc.scaleConstraint(secondary_global_control.C, self.modules_GRP)
    
        # make main control
        main_control_position = secondary_global_control.C
        main_control = control.Control(
                                      prefix = character_name + '_main',
                                      scale = scale * .12,
                                      parent = secondary_global_control.C,
                                      translate_to = main_control_position,
                                      shape = 'gear',
                                      locked_channels = ['visibility', 'translate', 'rotate', 'scale']
                                      )  
        #self._adjust_main_control_shape( main_control, scale )
                     
        main_visibility_attributes = ['geometry_visibility', 'joint_visibility']
        main_display_type_attributes = ['geometry_display', 'joint_display']
        main_object_list = [self.geo_GRP, self.skeleton_GRP]
        main_object_visibility_default_value_list = [1,1]
        main_object_display_type_default_value_list = [2,2]
        
        # add rig visibility connections
        for attribute, object, default_value in zip( main_visibility_attributes, main_object_list, main_object_visibility_default_value_list ):
            mc.addAttr( main_control.C, ln=attribute, attributeType='enum', enumName = 'off:on', keyable=True, defaultValue = default_value )
            mc.setAttr( main_control.C + '.' + attribute, channelBox=True)
            mc.connectAttr( main_control.C + '.' + attribute, object + '.v' )

        # add rig display_type connections
        for attribute, object, default_value in zip( main_display_type_attributes, main_object_list, main_object_display_type_default_value_list ):
            mc.addAttr( main_control.C, ln=attribute, attributeType='enum', enumName = 'normal:template:reference:proxy', keyable=True, defaultValue=default_value )
            mc.setAttr( main_control.C + '.' + attribute, channelBox=True)
            mc.setAttr( object + '.ove', True )
            mc.connectAttr( main_control.C + '.' + attribute, object + '.ovdt' )
        
        # create two condition nodes and a MD node for proxy/render geo display
        mc.shadingNode('multiplyDivide', asUtility=True, name= character_name + '_render_geo_display_MD_01')
        mc.connectAttr( main_control.C + '.geometry_visibility', character_name + '_render_geo_display_MD_01.input1X', force=True)
        mc.connectAttr( main_control.C + '.geometry_visibility', character_name + '_render_geo_display_MD_01.input1Y', force=True)
        
        mc.shadingNode('condition', asUtility=True, name= character_name + '_proxy_display_COND_01')
        mc.setAttr( character_name + '_proxy_display_COND_01.operation', 1)
        mc.connectAttr( main_control.C + '.geometry_display', character_name + '_proxy_display_COND_01.firstTerm', force=True)
        mc.setAttr( character_name + '_proxy_display_COND_01.secondTerm', 3)
        mc.connectAttr( character_name + '_render_geo_display_MD_01.outputY',  character_name + '_PROXY_GRP_01.visibility', force=True)
              
        mc.shadingNode('condition', asUtility=True, name= character_name + '_render_geo_display_COND_01')
        mc.setAttr( character_name + '_render_geo_display_COND_01.operation', 0)
        mc.connectAttr( main_control.C + '.geometry_display', character_name + '_render_geo_display_COND_01.firstTerm', force=True)
        mc.setAttr( character_name + '_render_geo_display_COND_01.secondTerm', 3)
        mc.connectAttr( character_name + '_render_geo_display_COND_01.outColor.outColorR', character_name + '_render_geo_display_MD_01.input2X', force=True)
        mc.connectAttr( character_name + '_proxy_display_COND_01.outColor.outColorR', character_name + '_render_geo_display_MD_01.input2Y', force=True)
        mc.connectAttr( character_name + '_render_geo_display_MD_01.outputX', character_name + '_geo_GRP_01.v', force=True)
        
        
        # make MD node for finding final scale of rig
        mc.shadingNode('multiplyDivide', asUtility=True, name= character_name + '_secret_total_scale_MD_01')
        mc.setAttr( character_name + '_secret_total_scale_MD_01.operation', 1)
        mc.connectAttr( character_name + '_secret_scale_os_grp_01.scale', character_name + '_secret_total_scale_MD_01.input1')
        mc.connectAttr( character_name + '_primary_global_cc_01.scale', character_name + '_secret_total_scale_MD_01.input2')

        
    def _flatten_global_control_shape( self, control_object ):
        
        #flatten control object shape
        control_shapes = mc.listRelatives( control_object, shapes=True, type = 'nurbsCurve' )
        cluster = mc.cluster( control_shapes )[1]
        mc.setAttr(cluster + '.rz', 90)
        mc.delete( control_shapes, constructionHistory=True)
        
    #def _adjust_main_control_shape(self, control, scale ):
        
        # adjust shape of main control
        #control_shapes = mc.listRelatives( control.C, shapes=True, type = 'nurbsCurve' )
        #cluster = mc.cluster( control_shapes )[1]
        #mc.delete( control_shapes, constructionHistory=True)


"""
Class for building a self-contained module to hold the rig element and be placed into the rig's structure
"""
class Module():
    
    def __init__(
                 self,
                 prefix = 'new', 
                 base_object = None            
                 ):
        
        """
        @param prefix: str, prefix to name new objects
        @base_object: instance of base.module.Base class to be new module's parent
        @return: None
        """
        
        self.top_GRP = mc.group( name=prefix + '_module_GRP_01', empty = True )
        self.controls_GRP = mc.group( name=prefix + '_controls_GRP_01', empty = True, p = self.top_GRP )
        self.skeleton_GRP = mc.group( name=prefix + '_skeleton_GRP_01', empty = True, p = self.top_GRP )
        self.extras_GRP = mc.group( name= 'extras_GRP_01', empty = True, parent=self.top_GRP )   
        mc.setAttr( self.extras_GRP + '.inheritsTransform', False, lock=True) 
            
        # parent module
        if base_object:
            mc.parent(self.top_GRP, base_object.modules_GRP)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        