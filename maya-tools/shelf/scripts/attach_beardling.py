import pymel.core as pm
from byugui import message_gui
import maya.mel as mel

def go():
	mel.eval(attachBeardling())

def attachBeardling():
	return '''
	string $constraint = "beardling_rig_main_Viking_main_cc_01.ConstraintSpace";

    // Parent head to head
    string $head = "beowulf_rig_main_Beowulf_head_cc_01" ;
    select -r $head;
    select -tgl "beardling_rig_main_Viking_head_controls_GRP_01" ;
    string $parented_head[] = `parentConstraint -mo -weight 1`;
    connectAttr -f $constraint ($parented_head[0] + "." + $head + "W0");

    // Parent main body to chest
    string $chest = "beowulf_rig_main_Beowulf_chest_cc_01" ;
    select -r $chest;
    select -tgl "beardling_rig_main_Viking_controls_GRP_01" ;
    string $parented_chest[] = `parentConstraint -mo -weight 1`;
    connectAttr -f $constraint ($parented_chest[0] + "." + $chest + "W0");

    // Parent hands to head
    select -r $head;
    select -tgl "beardling_rig_main_Viking_LFT_IK_arm_cc_os_grp_01" ;
    string $parented_left[] = `parentConstraint -mo -weight 1`;
    connectAttr -f $constraint ($parented_left[0] + "." + $head + "W0");

    select -r $head;
    select -tgl "beardling_rig_main_Viking_RGT_IK_arm_cc_os_grp_01" ;
    string $parented_right[] = `parentConstraint -mo -weight 1`;
    connectAttr -f $constraint ($parented_right[0] + "." + $head + "W0");

    select -clear;
	'''
