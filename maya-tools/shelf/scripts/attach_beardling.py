import pymel.core as pm
from byugui import message_gui
import maya.mel as mel

def go():
	mel.eval(attachBeardling())

def attachBeardling():
	return '''
	// Parent head to head
    select -r "beowulf_rig_main_Beowulf_head_cc_01" ;
    select -tgl "beardling_rig_main_Viking_head_cc_01" ;
    doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","0","1","","1" };
    parentConstraint -mo -weight 1;

    // Parent main body to chest
    select -r "beowulf_rig_main_Beowulf_chest_cc_01" ;
    select -tgl "beardling_rig_main_Viking_primary_global_cc_01" ;
    doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","0","1","","1" };
    parentConstraint -mo -weight 1;

    // Parent hands to head
    select -r beowulf_rig_main_Beowulf_head_cc_01 ;
    select -tgl beardling_rig_main_Viking_LFT_IK_arm_cc_01 ;
    doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","0","1","","1" };
    parentConstraint -mo -weight 1;

    select -r beowulf_rig_main_Beowulf_head_cc_01 ;
    select -tgl beardling_rig_main_Viking_RGT_IK_arm_cc_01 ;
    doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","0","1","","1" };
    parentConstraint -mo -weight 1;

    select -clear;
	'''
