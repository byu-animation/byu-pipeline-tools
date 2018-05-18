"""
Module for making rig controls.
"""

import maya.cmds as mc

"""
Class for building rig control
"""
class Control():

    def __init__(
               self,
               prefix = 'new',
               scale = 1.0,
               use_numerical_transforms = False,
               transform_x = 0.0,
               transform_y = 0.0,
               transform_z = 0.0,
               translate_to = '',
               rotate_to = '',
               parent = '',
               shape = 'circle',
               locked_channels = ['scale', 'visibility']
              ):


        """
        @param prefix: str, prefix to name new objects
        @param scale: float, scale value for size of control shapes
        @param use_numerical_transforms: boolean, match transforms of control to user-provided numbers instead of an object
        @param transform_x: float, relative x translate values for new control
        @param transform_y: float, relative y translate values for new control
        @param transform_z: float, relative z translate values for new control
        @param translate_to: str, reference object for control position
        @param rotate_to: str, reference object for control rotation
        @param parent: str, object to be parent of new control
        @param shape: str, controls control curve shape type.
        @param locked_channels: list(str), list of channels on control to be locked and potentially non-keyable.
        @return: None
        """


        # make differently shaped nurbs control curves
        # turn off soft selection
        mc.softSelect(sse=False)

        if shape in ['circle', 'circle_x']:
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [1,0,0], radius = scale )[0]

        elif shape == 'circle_y':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [0,1,0], radius = scale )[0]

        elif shape == 'circle_z':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [0,0,1], radius = scale )[0]

        elif shape == 'square':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [1,0,0], radius = scale, sections=4, degree=1 )[0]
            mc.select( prefix + '_cc_01Shape.cv[0:4]' )
            mc.rotate(-45.0,0.0,0.0)

        elif shape == 'square_y':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [0,1,0], radius = scale, sections=4, degree=1 )[0]
            mc.select( prefix + '_cc_01Shape.cv[0:4]' )
            mc.rotate(-45.0,0.0,0.0)

        elif shape == 'square_z':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [0,0,1], radius = scale, sections=4, degree=1 )[0]
            mc.select( prefix + '_cc_01Shape.cv[0:4]' )
            mc.rotate(-45.0,0.0,0.0)

        elif shape == 'diamond':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [1,0,0], radius = scale, sections=4, degree=1 )[0]
            mc.select( prefix + '_cc_01Shape.cv[0:4]' )
            mc.rotate(0.0,0.0,0.0)

        elif shape == 'diamond_y':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [0,1,0], radius = scale, sections=4, degree=1 )[0]
            mc.select( prefix + '_cc_01Shape.cv[0:4]' )
            mc.rotate(0.0,0.0,0.0)

        elif shape == 'diamond_z':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [0,0,1], radius = scale, sections=4, degree=1 )[0]
            mc.select( prefix + '_cc_01Shape.cv[0:4]' )
            mc.rotate(0.0,0.0,0.0)

        elif shape == 'box':
            #top
            mc.curve( point=[(-0.5*scale,0.5*scale,0.5*scale), (0.5*scale,0.5*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_cc_01')
            mc.curve( point=[(-0.5*scale,0.5*scale,-0.5*scale), (0.5*scale,0.5*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_1_cc_01' )
            mc.curve( point=[(-0.5*scale,0.5*scale,0.5*scale), (-0.5*scale,0.5*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_2_cc_01' )
            mc.curve( point=[(0.5*scale,0.5*scale,-0.5*scale), (0.5*scale,0.5*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_3_cc_01' )
            #bottom
            mc.curve( point=[(-0.5*scale,-0.5*scale,0.5*scale), (0.5*scale,-0.5*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_4_cc_01' )
            mc.curve( point=[(-0.5*scale,-0.5*scale,-0.5*scale), (0.5*scale,-0.5*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_5_cc_01' )
            mc.curve( point=[(-0.5*scale,-0.5*scale,0.5*scale), (-0.5*scale,-0.5*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_6_cc_01' )
            mc.curve( point=[(0.5*scale,-0.5*scale,-0.5*scale), (0.5*scale,-0.5*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_7_cc_01' )
            #sides
            mc.curve( point=[(-0.5*scale,-0.5*scale,0.5*scale), (-0.5*scale,0.5*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_8_cc_01' )
            mc.curve( point=[(-0.5*scale,-0.5*scale,-0.5*scale), (-0.5*scale,0.5*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_9_cc_01' )
            mc.curve( point=[(0.5*scale,-0.5*scale,0.5*scale), (0.5*scale,0.5*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_10_cc_01' )
            mc.curve( point=[(0.5*scale,-0.5*scale,-0.5*scale), (0.5*scale,0.5*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_11_cc_01' )
            #combine
            control_object = prefix + '_cc_01'
            for number in range(1,12):
                mc.parent( mc.listRelatives( prefix + '_' + str(number) + '_cc_01', shapes=True ), control_object, relative=True, shape=True)
                mc.delete(prefix + '_' + str(number) + '_cc_01')

        elif shape == 'sphere':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [1,0,0], radius = scale )[0]
            control_object_add_a = mc.circle( name = prefix + '_cc_a_01', ch=False,  normal = [0,1,0], radius = scale )[0]
            control_object_add_b = mc.circle( name = prefix + '_cc_b_01', ch=False,  normal = [0,0,1], radius = scale )[0]
            mc.parent( mc.listRelatives( control_object_add_a, shapes=True ), control_object, relative=True, shape=True)
            mc.parent( mc.listRelatives( control_object_add_b, shapes=True ), control_object, relative=True, shape=True)
            mc.delete(control_object_add_a)
            mc.delete(control_object_add_b)

        elif shape == 'gear':
            mc.circle(radius=0.25*scale, normal=[0,1,0], name = prefix + '_cc_01')
            mc.circle(radius=0.5*scale, normal=[0,1,0], sections=72, name = prefix + '_add_cc_01')
            mc.select( prefix + '_add_cc_01.cv[5:9]', replace=True )
            mc.select( prefix + '_add_cc_01.cv[17:21]', add=True )
            mc.select( prefix + '_add_cc_01.cv[29:33]', add=True )
            mc.select( prefix + '_add_cc_01.cv[41:46]', add=True )
            mc.select( prefix + '_add_cc_01.cv[53:57]', add=True )
            mc.select( prefix + '_add_cc_01.cv[65:69]', add=True )
            mc.scale(0.75,0.75,0.75)
            mc.select( clear=True )
            control_object = prefix + '_cc_01'
            mc.parent( mc.listRelatives( prefix + '_add_cc_01', shapes=True ), control_object, relative=True, shape=True)
            mc.delete(prefix + '_add_cc_01')

        elif shape == 'pin':
            #bottom
            mc.curve( point=[(-0.5*scale,2.0*scale,0.5*scale), (0.5*scale,2.0*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_cc_01' )
            mc.curve( point=[(-0.5*scale,2.0*scale,-0.5*scale), (0.5*scale,2.0*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_1_cc_01' )
            mc.curve( point=[(-0.5*scale,2.0*scale,0.5*scale), (-0.5*scale,2.0*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_2_cc_01' )
            mc.curve( point=[(0.5*scale,2.0*scale,-0.5*scale), (0.5*scale,2.0*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_3_cc_01' )
            #sides
            mc.curve( point=[(-0.5*scale,2.0*scale,0.5*scale), (0.0*scale,3.0*scale,0.0*scale)], knot=[0,1], degree=1, name= prefix + '_4_cc_01' )
            mc.curve( point=[(-0.5*scale,2.0*scale,-0.5*scale), (0.0*scale,3.0*scale,0.0*scale)], knot=[0,1], degree=1, name= prefix + '_5_cc_01' )
            mc.curve( point=[(0.5*scale,2.0*scale,0.5*scale), (0.0*scale,3.0*scale,0.0*scale)], knot=[0,1], degree=1, name= prefix + '_6_cc_01' )
            mc.curve( point=[(0.5*scale,2.0*scale,-0.5*scale), (0.0*scale,3.0*scale,0.0*scale)], knot=[0,1], degree=1, name= prefix + '_7_cc_01' )
            #stem
            mc.curve( point=[(-0.5*scale,2.0*scale,-0.5*scale), (0.5*scale,2.0*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_8_cc_01' )
            mc.curve( point=[(-0.5*scale,2.0*scale,0.5*scale), (0.5*scale,2.0*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_9_cc_01' )
            mc.curve( point=[(0.0*scale,0.0*scale,0.0*scale), (0.0*scale,2.0*scale,0.0*scale)], knot=[0,1], degree=1, name= prefix + '_10_cc_01' )
            #combine
            control_object = prefix + '_cc_01'
            for number in range(1,11):
                mc.parent( mc.listRelatives( prefix + '_' + str(number) + '_cc_01', shapes=True ), control_object, relative=True, shape=True)
                mc.delete(prefix + '_' + str(number) + '_cc_01')

        elif shape == 'blunted_pin':
            #top
            mc.curve( point=[(-0.2*scale,3.0*scale,0.2*scale), (0.2*scale,3.0*scale,0.2*scale)], knot=[0,1], degree=1, name= prefix + '_cc_01')
            mc.curve( point=[(-0.2*scale,3.0*scale,-0.2*scale), (0.2*scale,3.0*scale,-0.2*scale)], knot=[0,1], degree=1, name= prefix + '_1_cc_01' )
            mc.curve( point=[(-0.2*scale,3.0*scale,0.2*scale), (-0.2*scale,3.0*scale,-0.2*scale)], knot=[0,1], degree=1, name= prefix + '_2_cc_01' )
            mc.curve( point=[(0.2*scale,3.0*scale,-0.2*scale), (0.2*scale,3.0*scale,0.2*scale)], knot=[0,1], degree=1, name= prefix + '_3_cc_01' )
            #bottom
            mc.curve( point=[(-0.5*scale,2.0*scale,0.5*scale), (0.5*scale,2.0*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_4_cc_01' )
            mc.curve( point=[(-0.5*scale,2.0*scale,-0.5*scale), (0.5*scale,2.0*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_5_cc_01' )
            mc.curve( point=[(-0.5*scale,2.0*scale,0.5*scale), (-0.5*scale,2.0*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_6_cc_01' )
            mc.curve( point=[(0.5*scale,2.0*scale,-0.5*scale), (0.5*scale,2.0*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_7_cc_01' )
            #sides
            mc.curve( point=[(-0.5*scale,2.0*scale,0.5*scale), (-0.2*scale,3.0*scale,0.2*scale)], knot=[0,1], degree=1, name= prefix + '_8_cc_01' )
            mc.curve( point=[(-0.5*scale,2.0*scale,-0.5*scale), (-0.2*scale,3.0*scale,-0.2*scale)], knot=[0,1], degree=1, name= prefix + '_9_cc_01' )
            mc.curve( point=[(0.5*scale,2.0*scale,0.5*scale), (0.2*scale,3.0*scale,0.2*scale)], knot=[0,1], degree=1, name= prefix + '_10_cc_01' )
            mc.curve( point=[(0.5*scale,2.0*scale,-0.5*scale), (0.2*scale,3.0*scale,-0.2*scale)], knot=[0,1], degree=1, name= prefix + '_11_cc_01' )
            #stem
            mc.curve( point=[(-0.5*scale,2.0*scale,-0.5*scale), (0.5*scale,2.0*scale,0.5*scale)], knot=[0,1], degree=1, name= prefix + '_12_cc_01' )
            mc.curve( point=[(-0.5*scale,2.0*scale,0.5*scale), (0.5*scale,2.0*scale,-0.5*scale)], knot=[0,1], degree=1, name= prefix + '_13_cc_01' )
            mc.curve( point=[(0.0*scale,0.0*scale,0.0*scale), (0.0*scale,2.0*scale,0.0*scale)], knot=[0,1], degree=1, name= prefix + '_14_cc_01' )
            #combine
            control_object = prefix + '_cc_01'
            for number in range(1,15):
                mc.parent( mc.listRelatives( prefix + '_' + str(number) + '_cc_01', shapes=True ), control_object, relative=True, shape=True)
                mc.delete(prefix + '_' + str(number) + '_cc_01')

        elif shape == 'spherical_target':
            control_object = mc.curve( point=[(0.0*scale,0.75*scale,0.0*scale), (0.0*scale,-0.75*scale,0.0*scale)], knot=[0,1], degree=1, name = prefix + '_cc_01' )
            control_object_add_a = mc.curve( point=[(0.75*scale,0.0*scale,0.0*scale), (-0.75*scale,0.0*scale,0.0*scale)], knot=[0,1], degree=1, name = prefix + '_a_shape_01' )
            control_object_add_b = mc.curve( point=[(0.0*scale,0.0*scale,0.75*scale), (0.0*scale,0.0*scale,-0.75*scale)], knot=[0,1], degree=1, name = prefix + '_b_shape_01' )
            control_object_add_c = mc.circle( name = prefix + '_c_shape_01', ch=False,  normal = [1,0,0], radius = scale/2.0 )[0]
            control_object_add_d = mc.circle( name = prefix + '_d_shape_01', ch=False,  normal = [0,1,0], radius = scale/2.0 )[0]
            control_object_add_e = mc.circle( name = prefix + '_e_shape_01', ch=False,  normal = [0,0,1], radius = scale/2.0 )[0]
            mc.parent( mc.listRelatives( control_object_add_a, shapes=True ), control_object, relative=True, shape=True)
            mc.parent( mc.listRelatives( control_object_add_b, shapes=True ), control_object, relative=True, shape=True)
            mc.parent( mc.listRelatives( control_object_add_c, shapes=True ), control_object, relative=True, shape=True)
            mc.parent( mc.listRelatives( control_object_add_d, shapes=True ), control_object, relative=True, shape=True)
            mc.parent( mc.listRelatives( control_object_add_e, shapes=True ), control_object, relative=True, shape=True)
            mc.delete(control_object_add_a)
            mc.delete(control_object_add_b)
            mc.delete(control_object_add_c)
            mc.delete(control_object_add_d)
            mc.delete(control_object_add_e)

        if shape == 'oval':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [1,0,0], radius = scale )[0]
            control_shapes = mc.listRelatives( control_object, shapes=True, type = 'nurbsCurve' )
            cluster = mc.cluster( control_shapes )[1]
            mc.setAttr(cluster + '.scaleZ', 4)
            mc.delete( control_shapes, constructionHistory=True)

        if shape == 'oval_y':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [0,1,0], radius = scale )[0]
            control_shapes = mc.listRelatives( control_object, shapes=True, type = 'nurbsCurve' )
            cluster = mc.cluster( control_shapes )[1]
            mc.setAttr(cluster + '.scaleY', 4)
            mc.delete( control_shapes, constructionHistory=True)

        if shape == 'oval_z':
            control_object = mc.circle( name = prefix + '_cc_01', ch=False,  normal = [0,0,1], radius = scale )[0]
            control_shapes = mc.listRelatives( control_object, shapes=True, type = 'nurbsCurve' )
            cluster = mc.cluster( control_shapes )[1]
            mc.setAttr(cluster + '.scaleX', 4)
            mc.delete( control_shapes, constructionHistory=True)

        #create offset group for the control curve
        control_offset_grp = mc.group( name = prefix + '_cc_os_grp_01', empty = True)
        mc.parent( control_object, control_offset_grp)

        # color control curve
        control_shapes = mc.listRelatives( control_object, shapes=True )
        for control_shape in control_shapes:
            mc.setAttr( control_shape + '.overrideEnabled', True)
            if 'LFT' in str(control_object):
                mc.setAttr( control_shape + '.overrideColor', 6 )
                if 'settings' in str(control_object) or 'secondary' in str(control_object):
                    mc.setAttr( control_shape + '.overrideColor', 15 )
            elif 'RGT' in str(control_object):
                mc.setAttr( control_shape + '.overrideColor', 13 )
                if 'settings' in str(control_object) or 'secondary' in str(control_object):
                    mc.setAttr( control_shape + '.overrideColor', 12 )
            else:
                mc.setAttr( control_shape + '.overrideColor', 22 )
                if 'settings' in str(control_object) or 'secondary' in str(control_object):
                    mc.setAttr( control_shape + '.overrideColor', 25 )

        # parent control with offset group to parent object and zero out rotations
        if mc.objExists( parent ):
            mc.parent( control_offset_grp, parent )
            mc.rotate( 0,0,0, control_offset_grp, absolute=True)

        # translate control curve via offset group to match target
        if use_numerical_transforms==False:
            if mc.objExists( translate_to ):
                mc.delete( mc.pointConstraint(translate_to, control_offset_grp) )
        else:
            mc.move(transform_x, transform_y, transform_z, control_offset_grp, absolute=True, localSpace=True )

        # rotate control curve via offset group to match target
        if mc.objExists( rotate_to ):
            mc.delete( mc.orientConstraint(rotate_to, control_offset_grp) )


        # locking additional channels
        single_attribute_lock_list = []

        for locked_channel in locked_channels:
            if locked_channel in ['t','r','s']:
                for axis in ['x','y','z']:
                    attribute = locked_channel + axis
                    single_attribute_lock_list.append( attribute )
            else:
                single_attribute_lock_list.append( locked_channel )

        for attribute in single_attribute_lock_list:
            mc.setAttr( control_object + "." + attribute, lock=True, keyable=True)






        # add public members
        self.C = control_object
        self.Off = control_offset_grp
