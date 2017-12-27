import pymel.core as pm
from byugui import message_gui
import maya.mel as mel

def go():
	selection = pm.ls(selection=True)
	if len(selection) == 2:
		mel.eval(attachBeard())
	else:
		message_gui.error('Please Select the beard and then the viking.')

def attachBeard():
	return '''
	// Make sure to select the beard before the viking
	string $list[] = `ls -selection`;
	string $beard = `match "viking_beard_[0-9]+_rig_main_" $list[0] `;
	string $prefix = `match "[A-Za-z0-9_]*(:)*viking_with_facial_rig_main_(mb)*[0-9]*(:)*" $list[1] `;
	string $viking = `match "Viking_GRP_[0-9]+" $list[1] `;
	string $body = $prefix + $viking + "|" + $prefix + "Viking_geo_GRP_01" + "|" + $prefix + "Viking_GEO_GRP_01" + "|" + $prefix + "Viking_body_GEO_01";
	string $jaw = $prefix + $viking + "|" + $prefix + "Viking_facial_rig_GRP_01" + "|" + $prefix + "Viking_facial_controls_GRP_01" + "|" + $prefix + "Viking_facial_controls_head_constraint_os_grp_01" + "|" + $prefix + "Viking_jaw_cc_os_grp_01" + "|" + $prefix + "Viking_jaw_cc_01";
	string $head = $prefix + $viking + "|" + $prefix + "Viking_body_rig_GRP_01" + "|" + $prefix + "Viking_controls_GRP_01" + "|" + $prefix + "Viking_secret_scale_os_grp_01" + "|" + $prefix + "Viking_primary_global_cc_01" + "|" + $prefix + "Viking_secondary_global_cc_os_grp_01" + "|" + $prefix + "Viking_secondary_global_cc_01" + "|" + $prefix + "Viking_head_controls_GRP_01" + "|" + $prefix + "Viking_head_cc_os_grp_01" + "|" + $prefix + "Viking_head_cc_01";
	// Wrap deform beard base
	select -r ($beard+"beard_base");
	select -tgl ($body);
	doWrapArgList "7" { "1","0","1", "2", "1", "1", "0", "0" };
	string $wrap_array[] = `deformer -type wrap ($beard+"beard_base")`;
	string $wrap = $wrap_array[0];
	select -r $wrap;
	setAttr ($wrap+".autoWeightThreshold") 1;
	setAttr ($wrap+".exclusiveBind") 1;
	setAttr ($wrap+".maxDistance") .01;
	// Wrap deform stache base
	if( `objExists ($beard+"stache_base")` )
	{
	    select -r ($beard+"stache_base");
	    select -tgl ($body);
	    doWrapArgList "7" { "1","0","1", "2", "1", "1", "0", "0" };
	    $wrap_array = `deformer -type wrap ($beard+"stache_base")`;
	    $wrap = $wrap_array[0];
	    select -r $wrap;
	    setAttr ($wrap+".autoWeightThreshold") 1;
	    setAttr ($wrap+".exclusiveBind") 1;
	    setAttr ($wrap+".maxDistance") .01;
	}
	// Parent beard to jaw
	select -r ($jaw);
	select -tgl ($beard+"beard_master");
	doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","0","1","","1" };
	parentConstraint -mo -weight 1;
	// Parent stache to head
	select -r ($head);
	select -tgl ($beard+"stache_master");
	doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","0","1","","1" };
	parentConstraint -mo -weight 1;
	'''
