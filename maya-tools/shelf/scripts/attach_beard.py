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
	string $viking = `match "viking_with_facial_rig_main_" $list[1] `;
	// Wrap deform beard base
	select -r ($beard+"beard_base");
	select -tgl ($viking+"Viking_body_GEO_01");
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
	    select -tgl ($viking+"Viking_body_GEO_01");
	    doWrapArgList "7" { "1","0","1", "2", "1", "1", "0", "0" };
	    $wrap_array = `deformer -type wrap ($beard+"stache_base")`;
	    $wrap = $wrap_array[0];
	    select -r $wrap;
	    setAttr ($wrap+".autoWeightThreshold") 1;
	    setAttr ($wrap+".exclusiveBind") 1;
	    setAttr ($wrap+".maxDistance") .01;
	}
	// Parent beard to jaw
	select -r ($viking+"Viking_jaw_cc_01");
	select -tgl ($beard+"beard_master");
	doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","0","1","","1" };
	parentConstraint -mo -weight 1;
	// Parent stache to head
	select -r ($viking+"Viking_head_cc_01");
	select -tgl ($beard+"stache_master");
	doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","0","1","","1" };
	parentConstraint -mo -weight 1;
	'''
