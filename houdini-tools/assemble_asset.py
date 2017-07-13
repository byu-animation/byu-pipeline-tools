import hou
import os
# import pyqt_houdini
from PySide2 import QtGui, QtWidgets, QtCore

from byuam import Department, Project, Environment
from byugui.assemble_gui import AssembleWindow
from byuam.environment import AssetType
from byugui import error_gui

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

def create_set_menu(hideWhen=None, callback_script=None):
	item_gen_script='''
from byuam.project import Project

project = Project()
set_list = list()

sets = project.list_sets()

for set in sets:
	set_list.append(set)
	set_list.append(set.replace('_', ' ').title())

return set_list
	'''
	set_menu = hou.StringParmTemplate('set', 'Set', 1, item_generator_script=item_gen_script, menu_type=hou.menuType.Normal, script_callback=callback_script, script_callback_language=hou.scriptLanguage.Python)
	if hideWhen is not None:
		set_menu.setConditional( hou.parmCondType.HideWhen, "{ " + hideWhen + " }")
	return set_menu

def create_shot_menu(hideWhen=None, callback_script=None):
	script = '''
from byuam.project import Project

project = Project()
directory_list = list()

shots = project.list_shots()

for shot in shots:
	directory_list.append(shot)
	directory_list.append(shot)

return directory_list
	'''
	shot = hou.StringParmTemplate('shot', 'Shot', 1, item_generator_script=script, menu_type=hou.menuType.Normal, script_callback=callback_script, script_callback_language=hou.scriptLanguage.Python)
	if hideWhen is not None:
		shot.setConditional( hou.parmCondType.HideWhen, "{ " + hideWhen + " }")
	return shot

def assemble_set(project, environment, assembly, asset, checkout_file):
	print "This is a set"
	model = asset.get_element(Department.MODEL)

	# Get all of the static geo
	model_cache = model.get_cache_dir()
	model_cache = model_cache.replace(project.get_project_dir(), '$JOB')
	geo_files = [x for x in os.listdir(model.get_cache_dir()) if not os.path.isdir(x)]

	geo_files = clean_file_list(geo_files, '.abc')

	# Set up the nodes
	obj = hou.node('/obj')
	subnet = obj.createNode('subnet')

	# Set up the set parameters
	# Get the paramter template group from the current geo node
	hou_parm_template_group = subnet.parmTemplateGroup()
	# Create a folder for the set parameters
	set_folder = hou.FolderParmTemplate('set_options', 'Set Options', folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
	set_folder.addParmTemplate(create_set_menu())

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
			print "There is not asset named " + asset_name + ". You may need to assemble it first."
			error_gui.error("There is not asset named " + asset_name + ". You may need to assemble it first.")
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


def addMaterialOptions(geo, groups):
	hou_parm_template_group = geo.parmTemplateGroup()
	material_folder = hou.FolderParmTemplate('materials', 'Material', folder_type=hou.folderType.Tabs)
	num_materials_folder = hou.FolderParmTemplate('num_materials', 'Number of Materials', folder_type=hou.folderType.MultiparmBlock)
	num_materials_folder.setDefaultValue(len(groups))

	script='''
	menu = ("one", "one", "two", "two")
	return menu

	'''

	group_names = list()
	for group in groups:
		group_names.append(group.name())

	groups = hou.StringParmTemplate('group#', 'Group', 1, menu_items=group_names, menu_type=hou.menuType.StringToggle)
	materials = hou.StringParmTemplate("mat_path#", "Material", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)

	num_materials_folder.addParmTemplate(groups)
	num_materials_folder.addParmTemplate(materials)

	material_folder.addParmTemplate(num_materials_folder)

	hou_parm_template_group.append(material_folder)
	geo.setParmTemplateGroup(hou_parm_template_group)
	return geo

def create_cook_button(geo):
	script='''
try:
	hou.node("./set_rig_alembic").cook(force=True)
except:
	print "Error while cooking set_rig_alembic"
try:
	hou.node("./set_model_alembic").cook(force=True)
except:
	print "Error while cooking set_model_alembic"
try:
	hou.node("./animaged_rig").cook(force=True)
except:
	print "Error while cooking animaged_rig"
try:
	hou.node("./animated_model").cook(force=True)
except:
	print "Error while cooking animated_model"

hou.node("./set_switch").cook(force=True)
hou.node("./shot_switch").cook(force=True)
	'''
	hou_parm_template_group = geo.parmTemplateGroup()
	cook = hou.ButtonParmTemplate('cook', 'ReCook', script_callback=script, script_callback_language=hou.scriptLanguage.Python)
	trouble_shoot_folder = hou.FolderParmTemplate('trouble_shoot', 'Trouble Shooting', folder_type=hou.folderType.Tabs)
	trouble_shoot_folder.addParmTemplate(cook)
	hou_parm_template_group.append(trouble_shoot_folder)
	geo.setParmTemplateGroup(hou_parm_template_group)
	return geo

def add_renderman_settings(geo, pxrdisplace):
	# Get the paramter template group from the current geo node
	hou_parm_template_group = geo.parmTemplateGroup()

	# Create a folder for the RenderMan parameters
	renderman_folder = hou.FolderParmTemplate('renderman', 'RenderMan', folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)

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

	return geo

def clean_file_list(file_paths, ext):
	# Remove anything from the list of file_paths that is not a file with the ext
	for file_path in list(file_paths):
		if not str(file_path).lower().endswith('.abc'):
			file_paths.remove(file_path)
	return file_paths

def set_up_ristnet(shop, name):
	risnet = shop.createNode('risnet')
	risnet.setName('risnet_' + name, unique_name=True)
	surface = risnet.createNode('pxrsurface')
	diffuse = surface.createInputNode(2, 'pxrtexture')

	displaceTex = risnet.createNode('pxrtexture')
	pxrtofloat = displaceTex.createOutputNode('pxrtofloat')
	pxrdisplace = risnet.createNode('pxrdisplace')

	pxrdisplace.setInput(1, pxrtofloat, 0)
	risnet.layoutChildren()
	return {'risnet': risnet, 'surface': surface, 'diffuse': diffuse, 'displaceTex': displaceTex, 'pxrdisplace': pxrdisplace}

def generate_groups_expression(group, model_name, rig_name):
	expression = '''prefix = ""

source = hou.ch("../../source")
input = hou.ch("../set_switch/input")

if source == 0:
	input = hou.ch("../set_switch/input")
elif source == 1:
	input = hou.ch("../shot_switch/input")
else:
	return hou.ch("../''' + group + '''")

if input == 1:
	prefix = "''' + model_name + '''_"
else:
	prefix = "''' + rig_name + '''_"

return prefix + str(hou.ch("../''' + group + '''"))
	'''
	return expression

def assemble(project, environment, assembly, asset, checkout_file):
	# Get assembly, model, and rig elements
	rig = asset.get_element(Department.RIG)
	model = asset.get_element(Department.MODEL)

	# Get all of the static geo
	model_cache = model.get_cache_dir()
	model_cache = model_cache.replace(project.get_project_dir(), '$JOB')
	geo_files = [x for x in os.listdir(model.get_cache_dir()) if not os.path.isdir(x)]

	geo_files = clean_file_list(geo_files, '.abc')

	if len(geo_files) > 1 or len(geo_files) < 1:
		error_gui.error("There was a problem importing the geo. Please re-export the geo from maya.")
		return

	geo_file = geo_files[0]

	# Set up the nodes
	obj = hou.node('/obj')
	subnet = obj.createNode('subnet')
	shop = subnet.createNode('shopnet', asset.get_name() + '_shopnet')
	name = ''.join(geo_file.split('.')[:-1])

	risnet_nodes = set_up_ristnet(shop, name)

	# Set up geo node
	geo_file_path = os.path.join(model_cache, geo_file)

	geo = subnet.createNode('geo')

	geo = add_renderman_settings(geo, risnet_nodes['pxrdisplace'])

	for child in geo.children():
		child.destroy()

	# Get rig or model info for each reference
	geo_file_name = os.path.basename(geo_file_path)
	# Some of the referenced geo is going to be from rigs and some is going to be from models so we need to plan for either to happen. Later we will add an expression that will use the alemibic that has geo in it.

	#I think these two lines where just from when we were still doing seperated peices
	#rig_reference = "/" + rig.get_long_name() + "_" + os.path.splitext(geo_file_name)[0]
	#model_reference = "/" + model.get_long_name() + "_" + os.path.splitext(geo_file_name)[0]

	# Alembic from selected set
	rig_model_set_switch = geo.createNode('switch')
	rig_model_set_switch.setName("set_switch")

	abc_set_rig = rig_model_set_switch.createInputNode(0, 'alembic')
	abc_set_rig.setName('set_rig_alembic')
	abc_set_rig.parm('fileName').setExpression('"$JOB/production/assets/" + chs("../../set") + "/model/main/cache/' + rig.get_long_name() + '.abc"')
	abc_set_rig.parm("groupnames").set(4)

	abc_set_model = rig_model_set_switch.createInputNode(1, 'alembic')
	abc_set_model.setName('set_model_alembic')
	abc_set_model.parm('fileName').setExpression('"$JOB/production/assets/" + chs("../../set") + "/model/main/cache/' + model.get_long_name() + '.abc"')
	abc_set_model.parm("groupnames").set(4)

	null_set = rig_model_set_switch.createInputNode(2, 'null')
	null_set.setName('no_set_model_found')

	# Object Space Alembic
	abc_object_space = geo.createNode('alembic')
	abc_object_space.setName("object_space_alembic")
	abc_object_space.parm('fileName').set(geo_file_path)
	abc_object_space.parm("groupnames").set(4)

	# Animated Alembics
	# Get all of the animated geo
	rig_model_switch = geo.createNode('switch')
	rig_model_switch.setName("shot_switch")

	abc_anim_rig = rig_model_switch.createInputNode(0, 'alembic')
	abc_anim_rig.setName('animaged_rig')
	abc_anim_rig.parm('fileName').setExpression('"$JOB/production/shots/" + chs("../../shot") + "/anim/main/cache/' + rig.get_long_name() + '.abc"')
	abc_anim_rig.parm("groupnames").set(4)
	# abc_anim_rig.parm('objectPath').set(rig_reference)

	abc_anim_model = rig_model_switch.createInputNode(1, 'alembic')
	abc_anim_model.setName("animated_model")
	abc_anim_model.parm('fileName').setExpression('"$JOB/production/shots/" + chs("../../shot") + "/anim/main/cache/' + model.get_long_name() + '.abc"')
	abc_anim_model.parm("groupnames").set(4)
	# abc_anim_model.parm('objectPath').set(model_reference)

	null_shot = rig_model_switch.createInputNode(2, 'null')
	null_shot.setName('no_shot_model_found')

	# Go through each input of each switch and if there is an error on the first node go to the next one and so on until you get to the last one which is just a null that won't have any errors
	rig_model_switch_expression = '''
import os

switch = hou.pwd()

i = 0

for node in switch.inputs():
    if len(node.errors()) > 0:
        i += 1
    else:
        return i
	'''
	rig_model_switch.parm('input').setExpression(rig_model_switch_expression, language=hou.exprLanguage.Python)
	rig_model_set_switch.parm('input').setExpression(rig_model_switch_expression, language=hou.exprLanguage.Python)


	switch = geo.createNode('switch')
	switch.parm('input').setExpression('ch("../../source_index")')
	switch.setInput(0, rig_model_set_switch)
	switch.setInput(1, rig_model_switch)
	switch.setInput(2, abc_object_space)

	convert = switch.createOutputNode('convert')

	hide_switch = convert.createOutputNode('switch')
	hide_switch.setName('hide_geo')
	null_geo = geo.createNode('null')
	hide_switch.setInput(1, null_geo)
	hide_switch.parm('input').setExpression('ch("../../hide")')

	geo = create_cook_button(geo)

	out = hide_switch.createOutputNode('null')
	out.setName('OUT')

	static_geo = abc_object_space.geometry()
	try:
		groups = static_geo.primGroups()
	except:
		error_gui.error("The static_geo has no groups.\n\n Details:\nstr(geometry) =  " + str(static_geo))
		print "This is what static_geo is and it's not working: " + str(static_geo)
	geo = addMaterialOptions(geo, groups)

	mat = out.createOutputNode('material')
	mat.setDisplayFlag(True)
	mat.setRenderFlag(True)
	mat.parm("num_materials").setExpression('ch("../num_materials")')
	for i, group in enumerate(groups):
		group_num = str(i + 1)
		geo.parm('group' + group_num).set(group.name())
		groupExpression = generate_groups_expression('group' + group_num, model.get_long_name(), rig.get_long_name())
		print groupExpression
		# geo.parm('group' + group_num).setExpression(groupExpression)
		mat.parm('group' + group_num).setExpression(groupExpression, language=hou.exprLanguage.Python)
		mat.parm('shop_materialpath' + group_num).setExpression('chsop("../mat_path' + group_num + '")')

	geo.setName(name, unique_name=True)
	geo.layoutChildren()

	cook_script='hou.node("./' + name + '").parm("cook").pressButton()'
	print cook_script

	# Finish setting up the subnet and create digital asset
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
	projectName = project.get_name().lower().replace(" ", "_")
	projectFolder = hou.FolderParmTemplate(projectName, project.get_name(), folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)

	source_menu = hou.MenuParmTemplate('source', 'Source', ('set', 'animated', 'object_space'), menu_labels=('Set', 'Animated', 'Object Space'))
	source_menu_index = hou.IntParmTemplate('source_index', 'Source Index', 1, is_hidden=True)

	projectFolder.addParmTemplate(source_menu)
	projectFolder.addParmTemplate(source_menu_index)
	projectFolder.addParmTemplate(create_shot_menu(hideWhen='source_index != 1', callback_script=cook_script))
	projectFolder.addParmTemplate(create_set_menu(hideWhen='source_index != 0', callback_script=cook_script))
	hide_check = hou.ToggleParmTemplate("hide", "Hide")
	animated_toggle = hou.ToggleParmTemplate("animate", "Animated")
	projectFolder.addParmTemplate(hide_check)
	projectFolder.addParmTemplate(animated_toggle)
	parmGroup.addParmTemplate(projectFolder)
	asset.type().definition().setParmTemplateGroup(parmGroup)

	# since the shot and set parms are technially srings and not really menus we need to set them to be the first string so they don't come in blank
	first_shot = str(project.list_shots()[0])
	first_set = str(project.list_sets()[0])
	asset.parm('shot').set(first_shot)
	asset.parm('set').set(first_set)
	asset.parm('source_index').setExpression('ch("source")')


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
