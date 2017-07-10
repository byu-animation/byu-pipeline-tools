import hou
import os
# import pyqt_houdini
from PySide2 import QtGui, QtWidgets, QtCore

from byuam import Department, Project, Environment
from byugui.assemble_gui import AssembleWindow
from byuam.environment import AssetType

def assemble_hda():
	asset_name = checkout_window.result

	if asset_name is None:
		return

	project = Project()
	environment = Environment()
	username = project.get_current_username()
	asset = project.get_asset(asset_name)
	assembly = asset.get_element(Department.ASSEMBLY)
	# Checkout assembly
	checkout_file = assembly.checkout(username)

	if asset.get_type() == AssetType.SET:
		assemble_set(project, environment, assembly, asset, checkout_file)
	else:
		assemble(project, environment, assembly, asset, checkout_file)

def create_shot_menu():
	script = '''
from byuam.project import Project

project = Project()
directory_list = list()

shots = project.list_shots()

#directory_list.append("static")
#directory_list.append("static")

for shot in shots:
	directory_list.append(shot)
	directory_list.append(shot)

return directory_list
	'''
	shot = hou.StringParmTemplate('shot', 'Shot', 1, item_generator_script=script, menu_type=hou.menuType.Normal)
	return shot

def assemble_set(project, environment, assembly, asset, checkout_file):
	print "This is a set"
	model = asset.get_element(Department.MODEL)

	# Get all of the static geo
	model_cache = model.get_cache_dir()
	model_cache = model_cache.replace(project.get_project_dir(), '$JOB')
	geo_files = [x for x in os.listdir(model.get_cache_dir()) if not os.path.isdir(x)]

	# Remove anything that is not an alembic files
	for file_path in list(geo_files):
		if(not str(file_path).lower().endswith('.abc')):
			geo_files.remove(file_path)

	# Set up the nodes
	obj = hou.node('/obj')
	subnet = obj.createNode('subnet')

	# Set up the set parameters
	# Get the paramter template group from the current geo node
	hou_parm_template_group = subnet.parmTemplateGroup()
	# Create a folder for the set parameters
	set_folder = hou.FolderParmTemplate('stdswitcher4_1', 'Set Options', folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
	set_folder.addParmTemplate(create_shot_menu())

	used_hdas = set()
	for geo_file in geo_files:
		geo_file_path = os.path.join(model_cache, geo_file)
		name = ''.join(geo_file.split('.')[:-1])
		print name
		# TODO : what if it is a rig?
		index = name.find("_model")
		if(index < 0):
			index = name.find("_rig")
		if(index < 0):
			print "We couldn't find either a rig or a model for this asset. That means something went wrong or I need to rethink this tool."
		asset_name = name[:index]
		print asset_name
		if(asset_name in used_hdas):
			print used_hdas
			continue
		try:
			hda = subnet.createNode(asset_name + "_main")
		except:
			msgBox = QtWidgets.QMessageBox()
			msgBox.setText(msgBox.tr("There is not asset named " + asset_name + ". You may need to assemble it first."))
			msgBox.addButton(QtWidgets.QMessageBox.Ok)

			msgBox.exec_()
			print "There is not asset named " + asset_name + ". You may need to assemble it first."
			subnet.destroy()
			return
		used_hdas.add(asset_name)
		label_text = asset_name.replace('_', ' ').title()
		geo_label = hou.LabelParmTemplate(asset_name, label_text)
		hide_check_name = "hide_" + asset_name
		hide_check = hou.ToggleParmTemplate(hide_check_name, "Hide")
		animated_toggle_name = "animate_" + asset_name
		animated_toggle = hou.ToggleParmTemplate(animated_toggle_name, "Animated")
		set_folder.addParmTemplate(geo_label)
		set_folder.addParmTemplate(hide_check)
		set_folder.addParmTemplate(animated_toggle)
		hda.parm('hide').setExpression('ch("../' + hide_check_name + '")')
		hda.parm('animate').setExpression('ch("../' + animated_toggle_name + '")')
		hda.parm('shot').setExpression('chs("../shot")')

	hou_parm_template_group.append(set_folder)
	subnet.layoutChildren()
	# We problably don't need this anymore now that we are jumping right into digital asset creation.
	subnet.setName(asset.get_name(), unique_name=True)

	# For your convience the variables are labeled as they appear in the create new digital asset dialogue box in Houdini
	# I know at least for me it was dreadfully unclear that the description was going to be the name that showed up in the tab menu.
	# node by saving it to the 'checkout_file' it will put the working copy of the otl in the user folder in the project directory so
	# the working copy won't clutter up their personal otl space.
	operatorName = assembly.get_short_name()
	operatorLabel = (project.get_name() + ' ' + asset.get_name()).title()
	saveToLibrary = checkout_file

	asset = subnet.createDigitalAsset(name=operatorName, description=operatorLabel, hda_file_name=saveToLibrary)
	assetTypeDef = asset.type().definition()
	assetTypeDef.setIcon(environment.get_project_dir() + '/byu-pipeline-tools/assets/images/icons/hda-icon.png')
	assetTypeDef.setParmTemplateGroup(hou_parm_template_group)


def assemble(project, environment, assembly, asset, checkout_file):
	# Get assembly, model, and rig elements
	rig = asset.get_element(Department.RIG)
	model = asset.get_element(Department.MODEL)

	# Get all of the static geo
	model_cache = model.get_cache_dir()
	model_cache = model_cache.replace(project.get_project_dir(), '$JOB')
	geo_files = [x for x in os.listdir(model.get_cache_dir()) if not os.path.isdir(x)]
	# Remove anything that is not an alembic files
	for file_path in list(geo_files):
		if(not str(file_path).lower().endswith('.abc')):
			geo_files.remove(file_path)

	# Set up the nodes
	obj = hou.node('/obj')
	subnet = obj.createNode('subnet')
	shop = subnet.createNode('shopnet', asset.get_name() + '_shopnet')
	for geo_file in geo_files:
		geo_file_path = os.path.join(model_cache, geo_file)
		name = ''.join(geo_file.split('.')[:-1])

		risnet = shop.createNode('risnet')
		risnet.setName('risnet_' + name, unique_name=True)
		surface = risnet.createNode('pxrsurface')
		diffuse = surface.createInputNode(2, 'pxrtexture')

		displaceTex = risnet.createNode('pxrtexture')
		pxrtofloat = displaceTex.createOutputNode('pxrtofloat')
		pxrdisplace = risnet.createNode('pxrdisplace')

		pxrdisplace.setInput(1, pxrtofloat, 0)
		risnet.layoutChildren()

		geo = subnet.createNode('geo')

		# Get the paramter template group from the current geo node
		hou_parm_template_group = geo.parmTemplateGroup()

		# Create a folder for the RenderMan parameters
		renderman_folder = hou.FolderParmTemplate('stdswitcher4_1', 'RenderMan', folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)

		# Create a new parameter for RenderMan 'Displacement Shader'
		displacement_shader = hou.StringParmTemplate('shop_displacepath', 'Displacement Shader', 1, default_value=(['']), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script='', item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
		displacement_shader.setHelp('RiDisplace')
		displacement_shader.setTags({'opfilter': '!!SHOP/DISPLACEMENT!!', 'oprelative': '.', 'spare_category': 'Shaders'})
		renderman_folder.addParmTemplate(displacement_shader)

		# Create a new parameter for RenderMan 'Displacement Bound'
		displacement_bound = hou.FloatParmTemplate('ri_dbound', 'Displacement Bound', 1, default_value=([0]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
		displacement_bound.setHelp('Attribute: displacementbound/sphere')
		displacement_bound.setTags({'spare_category': 'Shading'})
		renderman_folder.addParmTemplate(displacement_bound)

		# Create a new parameter for RenderMan 'Interpolate Boundary'
		interpolate_boundary = hou.ToggleParmTemplate("ri_interpolateboundary", "Interpolate Boundary", default_value=False)
		interpolate_boundary.setHelp("RiSubdivisionMesh - interpolateboundary")
		interpolate_boundary.setTags({"spare_category": "Geometry"})
		renderman_folder.addParmTemplate(interpolate_boundary)

		# Create a new parameter for Render Man 'Render as Subdivision' option
		rendersubd = hou.ToggleParmTemplate('ri_rendersubd', 'Polygons as Subdivision (RIB)', default_value=False)
		rendersubd.setHelp('RiSubdivisionMesh')
		rendersubd.setTags({'spare_category': 'Geometry'})
		renderman_folder.addParmTemplate(rendersubd)

		hou_parm_template_group.append(renderman_folder)

		geo.setParmTemplateGroup(hou_parm_template_group)

		# Code for /obj/geo1/shop_displacepath parm
		hou_parm = geo.parm('shop_displacepath')
		hou_parm.lock(False)
		hou_parm.set(pxrdisplace.path())
		hou_parm.setAutoscope(False)

		# Code for ri_dbound parm
		hou_parm = geo.parm('ri_dbound')
		hou_parm.lock(False)
		hou_parm.set(0)
		hou_parm.setAutoscope(False)

		# Code for ri_interpolateboundary parm
		hou_parm = geo.parm("ri_interpolateboundary")
		hou_parm.lock(False)
		hou_parm.set(1)
		hou_parm.setAutoscope(False)

		# Code for ri_rendersubd parm
		hou_parm = geo.parm('ri_rendersubd')
		hou_parm.lock(False)
		hou_parm.set(1)
		hou_parm.setAutoscope(False)

		for child in geo.children():
			child.destroy()
		abcStatic = geo.createNode('alembic')
		abcStatic.setName("staticAlembic")
		abcStatic.parm('fileName').set(geo_file_path)
		# name groups in the alembic after the transfrom node names
		abcStatic.parm("groupnames").set(4)
		geo_file_name = os.path.basename(geo_file_path)

		switch = abcStatic.createOutputNode('switch')
		# switchExpression = '''{
		# 	if ( strcmp(chs("../../shot"),"static") ) {
		# 		return 1;
		# 	}
		# 	return 0;
		# }'''
		# switchExpression = 'ch("../../animate")'
		switch.parm('input').setExpression('ch("../../animate")')

		# Get all of the animated geo
		# Some of the animated geo is going to be from rigs and some is going to be from models so we need to plan for either to happen. Later we will add an expression that will use the alemibic that has geo in it.
		rig_reference = "/" + rig.get_long_name() + "_" + os.path.splitext(geo_file_name)[0]
		model_reference = "/" + model.get_long_name() + "_" + os.path.splitext(geo_file_name)[0]
		dynSwitch = switch.createInputNode(1, 'switch')
		abcDynRig = dynSwitch.createInputNode(0, 'alembic')
		abcDynRig.parm('fileName').setExpression('"$JOB/production/shots/" + chs("../../shot") + "/anim/main/cache/' + rig.get_long_name() + '.abc"')
		abcDynRig.parm('objectPath').set(rig_reference)
		abcDynModel = dynSwitch.createInputNode(1, 'alembic')
		abcDynModel.parm('fileName').setExpression('"$JOB/production/shots/" + chs("../../shot") + "/anim/main/cache/' + model.get_long_name() + '.abc"')
		abcDynModel.parm('objectPath').set(model_reference)
		# Set the switch to select the input with the most geo (theoretically this comparition should be between nothing and something or nothing and nothing. It is not meant to handle if there is geo on both sides)
		dynSwitchExpression = '''{
		    if ( npoints(opinputpath(".", 0)) > npoints(opinputpath(".", 1)) ) {
		        return 0;
		    }
		    return 1;
		}'''
		dynSwitch.parm('input').setExpression(dynSwitchExpression)

		convert = switch.createOutputNode('convert')

		hide_switch = convert.createOutputNode('switch')
		blast = convert.createOutputNode('blast')
		hide_switch.setInput(1, blast)
		hide_switch.parm('input').setExpression('ch("../../hide")')
		out = hide_switch.createOutputNode('null')

		out.setDisplayFlag(True)
		out.setRenderFlag(True)

		groups = out.geometry().primGroups()
		for group in groups:
			print group
			# TODO figure out how to make the material thing for each group
			# TODO take all of this out of the for each geo file loop
			print group.name()

		geo.setName(name, unique_name=True)


	subnet.layoutChildren()
	shop.layoutChildren()
	# We problably don't need this anymore now that we are jumping right into digital asset creation.
	subnet.setName(asset.get_name(), unique_name=True)

	# For your convience the variables are labeled as they appear in the create new digital asset dialogue box in Houdini
	# I know at least for me it was dreadfully unclear that the description was going to be the name that showed up in the tab menu.
	# node by saving it to the 'checkout_file' it will put the working copy of the otl in the user folder in the project directory so
	# the working copy won't clutter up their personal otl space.
	operatorName = assembly.get_short_name()
	operatorLabel = (project.get_name() + ' ' + asset.get_name()).title()
	saveToLibrary = checkout_file

	asset = subnet.createDigitalAsset(name=operatorName, description=operatorLabel, hda_file_name=saveToLibrary)
	assetTypeDef = asset.type().definition()
	assetTypeDef.setIcon(environment.get_project_dir() + '/byu-pipeline-tools/assets/images/icons/hda-icon.png')

	# Bellow are some lines that were with the old broken version of the code I don't know what they do or why we have them?
	# TODO figure out what these lines do and keep them if they are important and get rid of them if they are not.
	# For your convience I have included some of my confustions about them.
	# My only fear is that they acctually do something important and later this year I will find that this doesn't work (much like I did just now with the description option for the createDigitalAsset function) and I will want to know the fix.
	# I dont' know why we need to copy the type properties. Shouldn't it be that those properties come over when we create the asset in the first place?
	# subnet.type().definition().copyToHDAFile(checkout_file, new_name=assembly.get_long_name(), new_menu_name=asset_name)
	# Why on earth are we trying to install it? It should already show up for the user and s/he hasn't publihsed it yet so it shouldn't be published for anyone else yet.
	# hou.hda.installFile(checkout_file)

	parmGroup = asset.parmTemplateGroup()
	projectFolder = hou.FolderParmTemplate('stdswitcher4_1', project.get_name(), folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
	projectFolder.addParmTemplate(create_shot_menu())
	hide_check = hou.ToggleParmTemplate("hide", "Hide")
	animated_toggle = hou.ToggleParmTemplate("animate", "Animated")
	projectFolder.addParmTemplate(hide_check)
	projectFolder.addParmTemplate(animated_toggle)
	parmGroup.addParmTemplate(projectFolder)
	asset.type().definition().setParmTemplateGroup(parmGroup)
	asset.parm('shot').set('static')


def go():
	# checkout_window = CheckoutWindow()
	# app = QtGui.QApplication.instance()
	# if app is None:
	#	 app = QtGui.QApplication(['houdini'])
	global checkout_window
	checkout_window = AssembleWindow(hou.ui.mainQtWindow(), [Department.ASSEMBLY])
	checkout_window.finished.connect(assemble_hda)

	# asset_name = 'hello_world'
	# asset = project.get_asset(asset_name)
