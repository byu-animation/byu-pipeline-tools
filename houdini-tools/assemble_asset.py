import hou
import os
# import pyqt_houdini
from PySide2 import QtGui, QtWidgets, QtCore

from byuam import Department, Project, Environment
from byugui.assemble_gui import AssembleWindow
from byuam.body import AssetType
from byugui import message_gui
import checkout

def rego():
	'''
	reassembles the currently selected node. That means leaving all of the shop nets in place but throwing out the geo and bringing it in fresh.
	'''

	selection = hou.selectedNodes()

	if len(selection) > 1:
		message_gui.error("Please only select one item")
		return
	if len(selection) <1:
		message_gui.error("Please select an item to be reassembled")
		return

	hda = selection[0]

	name = hda.type().name()
	index = name.rfind("_")
	main = name[index:]
	asset_name = name[:index]

	if main.find("_main") == -1:
		message_gui.error("There was something wrong with the name. Try tabbing in the asset again and trying one more time.")
		return

	project = Project()
	environment = Environment()
	username = project.get_current_username()
	asset = project.get_asset(asset_name)
	assembly = asset.get_element(Department.ASSEMBLY)
	# Checkout assembly
	checkout_file = checkout.checkout_hda(hda, project, environment)
	reassemble(hda, project, environment, assembly, asset, checkout_file)

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

def create_set_menu(hideWhen=None, callback_script=None, hidden=False, value=None):
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
	project = Project()
	if(value == None):
		if len(project.list_sets()) < 1:
			message_gui.error("There are currently no sets in created in the film. Because of how this node works you are going to have to create at least one set before assembling anything.")
			raise("No sets in the project")
		default_set = (str(project.list_sets()[0]),)
	else:
		default_set = (value,)
	print default_set
	set_menu = hou.StringParmTemplate('set', 'Set', 1, item_generator_script=item_gen_script, is_hidden=hidden, menu_type=hou.menuType.Normal, script_callback=callback_script, script_callback_language=hou.scriptLanguage.Python, default_value=default_set)
	print set_menu.defaultValue()
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
	project = Project()
	first_shot = (str(project.list_shots()[0]),)
	print first_shot
	shot = hou.StringParmTemplate('shot', 'Shot', 1, item_generator_script=script, menu_type=hou.menuType.Normal, script_callback=callback_script, script_callback_language=hou.scriptLanguage.Python, default_value=first_shot)
	print shot.defaultValue()
	if hideWhen is not None:
		shot.setConditional( hou.parmCondType.HideWhen, "{ " + hideWhen + " }")
	return shot

def assemble_set(project, environment, assembly, asset, checkout_file):
	set_hda = create_hda(asset, assembly, project, environment, checkout_file)
	print "This is a set"
	model = asset.get_element(Department.MODEL)

	# Get all of the static geo
	model_cache = model.get_cache_dir()
	model_cache = model_cache.replace(project.get_project_dir(), '$JOB')
	geo_files = [x for x in os.listdir(model.get_cache_dir()) if not os.path.isdir(x)]

	geo_files = clean_file_list(geo_files, '.abc')

	# Set up the set parameters
	# Create a folder for the set parameters
	set_folder = hou.FolderParmTemplate('set_options', 'Set Options', folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
	set_folder.addParmTemplate(create_set_menu(hidden=True, value=asset.get_name()))
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
			hda = set_hda.createNode(asset_name + "_main")
		except:
			message = "There is not asset named " + asset_name + ". You may need to assemble it first."
			print message
			message_gui.error(message)
			message_gui.error("Here is an extra error message just incase the first one was blank.\nThere is an asset that hasn't been assembled yet and that is why this fails.")
			hda.destroy()
			return
		used_hdas.add(asset_name)
		label_text = asset_name.replace('_', ' ').title()
		geo_label = hou.LabelParmTemplate(asset_name, label_text)
		hide_toggle_name = "hide_" + asset_name
		hide_toggle = hou.ToggleParmTemplate(hide_toggle_name, "Hide")
		animate_toggle_name = "animate_" + asset_name
		animate_toggle = hou.ToggleParmTemplate(animate_toggle_name, "Animate")
		animate_toggle_to_int_name = "animate_toggle_to_int_" + asset_name
		animate_toggle_to_int = hou.IntParmTemplate(animate_toggle_to_int_name, 'Toggle To Int', 1, is_hidden=True, default_expression=('ch("' + animate_toggle_name + '")',))
		set_folder.addParmTemplate(geo_label)
		set_folder.addParmTemplate(hide_toggle)
		set_folder.addParmTemplate(animate_toggle)
		set_folder.addParmTemplate(animate_toggle_to_int)
		hda.parm('hide').setExpression('ch("../' + hide_toggle_name + '")')
		hda.parm('shot').setExpression('chs("../shot")')
		hda.parm('set').setExpression('chs("../set")')
		hda.parm('source').setExpression('chs("../' + animate_toggle_to_int_name + '")')

	assetTypeDef = set_hda.type().definition()
	hda_parm_group = assetTypeDef.parmTemplateGroup()
	hda_parm_group.append(set_folder)
	assetTypeDef.setParmTemplateGroup(hda_parm_group)

	set_hda.layoutChildren()

def addMaterialOptions(geo, groups):
	hou_parm_template_group = geo.parmTemplateGroup()
	material_folder = hou.FolderParmTemplate('materials', 'Material', folder_type=hou.folderType.Tabs)
	num_materials_folder = hou.FolderParmTemplate('num_materials', 'Number of Materials', folder_type=hou.folderType.MultiparmBlock)
	num_materials_folder.setDefaultValue(len(groups))

	group_names = list()
	for group in groups:
		group_names.append(group.name())

	groups = hou.StringParmTemplate('group#', 'Group', 1, menu_items=group_names, menu_type=hou.menuType.StringToggle)
	materials = hou.StringParmTemplate("mat_path#", "Material", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	# Create a new parameter for RenderMan 'Displacement Shader'
	displacement_shader = hou.StringParmTemplate('shop_displacepath#', 'Displacement Shader', 1, default_value=(['']), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script='', item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	displacement_shader.setHelp('RiDisplace')
	displacement_shader.setTags({'oprelative': '.'})
	# Create a new parameter for RenderMan 'Displacement Bound'
	displacement_bound = hou.FloatParmTemplate('ri_dbound#', 'Displacement Bound', 1, default_value=([0]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
	displacement_bound.setHelp('Attribute: displacementbound/sphere')
	displacement_bound.setTags({'spare_category': 'Shading'})

	num_materials_folder.addParmTemplate(groups)
	num_materials_folder.addParmTemplate(materials)
	num_materials_folder.addParmTemplate(displacement_shader)
	num_materials_folder.addParmTemplate(displacement_bound)

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
	hou.node("./animated_rig").cook(force=True)
except:
	print "Error while cooking animated_rig"
try:
	hou.node("./animated_model").cook(force=True)
except:
	print "Error while cooking animated_model"

hou.node("./set_switch").cook(force=True)
hou.node("./shot_switch").cook(force=True)
	'''
	hou_parm_template_group = geo.parmTemplateGroup()
	cook = hou.ButtonParmTemplate('cook', 'Refresh', script_callback=script, script_callback_language=hou.scriptLanguage.Python)
	trouble_shoot_folder = hou.FolderParmTemplate('trouble_shoot', 'Trouble Shooting', folder_type=hou.folderType.Tabs)
	trouble_shoot_folder.addParmTemplate(cook)
	hou_parm_template_group.append(trouble_shoot_folder)
	geo.setParmTemplateGroup(hou_parm_template_group)
	return geo

def add_renderman_settings(geo, pxrdisplace=None, pxrdisplaceexpr=None, riboundExpr=None, add_displacement=False):
	# Get the paramter template group from the current geo node
	hou_parm_template_group = geo.parmTemplateGroup()

	# Create a folder for the RenderMan parameters
	renderman_folder = hou.FolderParmTemplate('renderman', 'RenderMan', folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)

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

	# TODO: If we can get the displacement to work by group then we don't need to have this here anymore. We will need to finish hooking it up in addMaterialOptions()
	if(add_displacement):
		# Create a new parameter for RenderMan 'Displacement Shader'
		displacement_shader = hou.StringParmTemplate('shop_displacepath', 'Displacement Shader', 1, default_value=(['']), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script='', item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
		displacement_shader.setHelp('RiDisplace')
		displacement_shader.setTags({'oprelative': '.','spare_category': 'Shading'})
		renderman_folder.addParmTemplate(displacement_shader)

		# Create a new parameter for RenderMan 'Displacement Bound'
		displacement_bound = hou.FloatParmTemplate('ri_dbound', 'Displacement Bound', 1, default_value=([0]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
		displacement_bound.setHelp('Attribute: displacementbound/sphere')
		displacement_bound.setTags({'spare_category': 'Shading'})
		renderman_folder.addParmTemplate(displacement_bound)

	hou_parm_template_group.append(renderman_folder)

	geo.setParmTemplateGroup(hou_parm_template_group)

	# TODO: If we can get the displacement to work by group then we don't need to have this here anymore. We will need to finish hooking it up in addMaterialOptions()
	if add_displacement:
		# Code for /obj/geo1/shop_displacepath parm
		hou_parm = geo.parm('shop_displacepath')
		hou_parm.lock(False)
		if pxrdisplace is not None:
			hou_parm.set(pxrdisplace.relativePathTo(geo))
		if pxrdisplaceexpr is not None:
			hou_parm.setExpression(pxrdisplaceexpr)
		hou_parm.setAutoscope(False)

		# Code for ri_dbound parm
		hou_parm = geo.parm('ri_dbound')
		hou_parm.lock(False)
		hou_parm.set(0)
		if riboundExpr is not None:
			hou_parm.setExpression(riboundExpr)
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

def ristnet_set_up(shop, name):
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

if input == 0:
	prefix = "''' + model_name + '''_"
else:
	prefix = "''' + rig_name + '''_"

return prefix + str(hou.ch("../''' + group + '''"))
	'''
	return expression

def create_hda(asset, assembly, project, environment, checkout_file):
	# Set up the nodes
	obj = hou.node('/obj')
	subnet = obj.createNode('subnet')
	subnet.setName(asset.get_name(), unique_name=True)

	# For your convience the variables are labeled as they appear in the create new digital asset dialogue box in Houdini
	# I know at least for me it was dreadfully unclear that the description was going to be the name that showed up in the tab menu.
	# node by saving it to the 'checkout_file' it will put the working copy of the otl in the user folder in the project directory so
	# the working copy won't clutter up their personal otl space.
	operatorName = assembly.get_short_name()
	operatorLabel = (project.get_name() + ' ' + asset.get_name()).title()
	saveToLibrary = checkout_file

	hda = subnet.createDigitalAsset(name=operatorName, description=operatorLabel, hda_file_name=saveToLibrary)
	assetTypeDef = hda.type().definition()
	assetTypeDef.setIcon(environment.get_project_dir() + '/byu-pipeline-tools/assets/images/icons/hda-icon.png')

	# Bellow are some lines that were with the old broken version of the code I don't know what they do or why we have them?
	# TODO figure out what these lines do and keep them if they are important and get rid of them if they are not.
	# For your convience I have included some of my confustions about them.
	# My only fear is that they acctually do something important and later this year I will find that this doesn't work (much like I did just now with the description option for the createDigitalAsset function) and I will want to know the fix.
	# I dont' know why we need to copy the type properties. Shouldn't it be that those properties come over when we create the asset in the first place?
	# subnet.type().definition().copyToHDAFile(checkout_file, new_name=assembly.get_long_name(), new_menu_name=asset_name)
	# Why on earth are we trying to install it? It should already show up for the user and s/he hasn't publihsed it yet so it shouldn't be published for anyone else yet.
	# hou.hda.installFile(checkout_file)
	return hda

def assemble(project, environment, assembly, asset, checkout_file):
	hda = create_hda(asset, assembly, project, environment, checkout_file)

	shop = hda.createNode('shopnet', asset.get_name() + '_shopnet')

	risnet_nodes = ristnet_set_up(shop, asset.get_name())
	shop.layoutChildren()

	# Set up geo node
	geo = geo_setup(hda, asset, project)

	# Finish setting up the hda
	hda.layoutChildren()
	hda = hda_parameter_setup(hda, geo, project)

def reassemble(hda, project, environment, assembly, asset, checkout_file):
	shop = hda.node(asset.get_name() + "_shopnet")

	geos = [c for c in hda.children() if c.type().name() == "geo"]
	for geo in geos:
		geo.destroy()

	touching = [c for c in hda.children() if c.name() == "dont_touch_this_subnet"]
	for touch in touching:
		touch.destroy()

	geo = geo_setup(hda, asset, project)

	hda.layoutChildren()
	hda = reset_parameters(hda)
	hda = hda_parameter_setup(hda, geo, project)

def reset_parameters(hda):
	subnet = hou.node("obj").createNode('subnet')
	parmGroup = subnet.parmTemplateGroup()
	hda.type().definition().setParmTemplateGroup(parmGroup)
	subnet.destroy()
	return hda

def hda_parameter_setup(hda, geo, project):
	parmGroup = hda.parmTemplateGroup()
	projectName = project.get_name().lower().replace(" ", "_")
	projectFolder = hou.FolderParmTemplate(projectName, project.get_name(), folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)

	source_menu = hou.MenuParmTemplate('source', 'Source', ('set', 'animated', 'object_space'), menu_labels=('Set', 'Animated', 'Object Space'), default_value=2)
	source_menu_index = hou.IntParmTemplate('source_index', 'Source Index', 1, is_hidden=True, default_expression=('ch("source")',))

	projectFolder.addParmTemplate(source_menu)
	projectFolder.addParmTemplate(source_menu_index)
	cook_script='hou.node("./' + geo.name() + '").parm("cook").pressButton()\nprint "Asset Refreshed"'
	projectFolder.addParmTemplate(create_shot_menu(hideWhen='source_index != 1', callback_script=cook_script))
	projectFolder.addParmTemplate(create_set_menu(hideWhen='source_index != 0', callback_script=cook_script))
	hide_toggle = hou.ToggleParmTemplate("hide", "Hide")
	projectFolder.addParmTemplate(hide_toggle)
	recook = hou.ButtonParmTemplate("re_cook_hda", "Reload", script_callback=cook_script, script_callback_language=hou.scriptLanguage.Python)
	projectFolder.addParmTemplate(recook)
	parmGroup.addParmTemplate(projectFolder)
	hda.type().definition().setParmTemplateGroup(parmGroup)

	return hda

def get_model_alembic_cache(model, project):
	# Get all of the static geo
	model_cache = model.get_cache_dir()
	model_cache = model_cache.replace(project.get_project_dir(), '$JOB')
	geo_files = [x for x in os.listdir(model.get_cache_dir()) if not os.path.isdir(x)]

	geo_files = clean_file_list(geo_files, '.abc')

	if len(geo_files) > 1 or len(geo_files) < 1:
		message_gui.error("There was a problem importing the geo. Please re-export the geo from maya.")
		return

	return geo_files[0]

def geo_setup(parentNode, asset, project):
	# Get assembly, model, and rig elements
	rig = asset.get_element(Department.RIG)
	model = asset.get_element(Department.MODEL)

	geo_file = get_model_alembic_cache(model, project)
	geo_file_path = os.path.join(model.get_cache_dir(), geo_file)

	geo = parentNode.createNode('geo')

	geo = add_renderman_settings(geo)

	for child in geo.children():
		child.destroy()

	# Get rig or model info for each reference
	# geo_file_name = os.path.basename(geo_file_path)
	# Some of the referenced geo is going to be from rigs and some is going to be from models so we need to plan for either to happen. Later we will add an expression that will use the alemibic that has geo in it.

	#I think these two lines where just from when we were still doing seperated peices
	#rig_reference = "/" + rig.get_long_name() + "_" + os.path.splitext(geo_file_name)[0]
	#model_reference = "/" + model.get_long_name() + "_" + os.path.splitext(geo_file_name)[0]

	# Alembic from selected set
	rig_model_set_switch = geo.createNode('switch')
	rig_model_set_switch.setName("set_switch")

	abc_set_model = rig_model_set_switch.createInputNode(0, 'alembic')
	abc_set_model.setName('set_model_alembic')
	abc_set_model.parm('fileName').setExpression('"$JOB/production/assets/" + chs("../../set") + "/model/main/cache/' + model.get_long_name() + '.abc"')
	abc_set_model.parm("groupnames").set(4)

	abc_set_rig = rig_model_set_switch.createInputNode(1, 'alembic')
	abc_set_rig.setName('set_rig_alembic')
	abc_set_rig.parm('fileName').setExpression('"$JOB/production/assets/" + chs("../../set") + "/model/main/cache/' + rig.get_long_name() + '.abc"')
	abc_set_rig.parm("groupnames").set(4)

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

	abc_anim_model = rig_model_switch.createInputNode(0, 'alembic')
	abc_anim_model.setName("animated_model")
	abc_anim_model.parm('fileName').setExpression('"$JOB/production/shots/" + chs("../../shot") + "/anim/main/cache/' + model.get_long_name() + '.abc"')
	abc_anim_model.parm("groupnames").set(4)
	# abc_anim_model.parm('objectPath').set(model_reference)

	abc_anim_rig = rig_model_switch.createInputNode(1, 'alembic')
	abc_anim_rig.setName('animated_rig')
	abc_anim_rig.parm('fileName').setExpression('"$JOB/production/shots/" + chs("../../shot") + "/anim/main/cache/' + rig.get_long_name() + '.abc"')
	abc_anim_rig.parm("groupnames").set(4)
	# abc_anim_rig.parm('objectPath').set(rig_reference)

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
		message_gui.error("The static_geo has no groups.\n\n Details:\nstr(geometry) =  " + str(static_geo))
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
		mat.parm('group' + group_num).setExpression(groupExpression, language=hou.exprLanguage.Python)
		mat.parm('shop_materialpath' + group_num).setExpression('chsop("../mat_path' + group_num + '")')

	geo.setName(asset.get_name(), unique_name=True)
	geo.layoutChildren()
	try:
		rig_model_set_switch.cook()
	except:
		try:
			rig_model_switch.cook()
		except:
			print "There was a problem with one of the things but I think that is okay"
	geo.cook()


	# Here is the temporary solution to the can't-assign-renderman-displacement-by-group-problem
	# In addition to getting rid of this code you will also need to implement the new way to do displacement by group if Renderman in Houdini ever gets that capability.
	# For example, in the future the displacement shader and bound would only need to be applied in the material parameter tab and not in the Renderman tab. But since we are using the same code for the geo nodes in the dont_touch_this_subnet subnet it doesn't make senese to remove it just yet.
	subnet = geo.parent().createNode("subnet")
	for i, group in enumerate(groups):
		group_num = str(i + 1)
		group_geo = subnet.createNode("geo")
		group_geo.setName(group.name())
		mat_path_expr = 'chsop("../../' + geo.name() + '/mat_path' + group_num + '")'
		displacePathExpr = 'chsop("../../' + geo.name() + '/shop_displacepath' + group_num + '")'
		riBoundExpr = 'ch("../../' + geo.name() + '/ri_dbound' + group_num + '")'
		group_geo = add_renderman_settings(group_geo, pxrdisplaceexpr=displacePathExpr, riboundExpr=riBoundExpr, add_displacement=True)
		group_geo.parm("shop_materialpath").setExpression(mat_path_expr)

		for child in group_geo.children():
			child.destroy()
		obj_merge = group_geo.createNode("object_merge")
		obj_merge.parm("objpath1").set("../../../" + geo.name() + "/" + out.name())
		blast = obj_merge.createOutputNode("blast")
		blast.parm("group").set(group.name())
		blast.parm("group").setExpression(generate_groups_expression_renameMe(group.name(), model.get_long_name(), rig.get_long_name(), geo.name()), language=hou.exprLanguage.Python)
		blast.parm("negate").set(True)
		blast.setRenderFlag(True)
		blast.setDisplayFlag(True)

	subnet.layoutChildren()
	subnet.setName("dont_touch_this_subnet")
	tempHideDisplay = geo.createNode("null")
	tempHideDisplay.setRenderFlag(True)
	tempHideDisplay.setDisplayFlag(True)
	# End temp solution

	return geo

def generate_groups_expression_renameMe(group, model_name, rig_name, asset_name):
	expression = '''
prefix = ""

source = hou.ch("../../../source")
input = hou.ch("../../../''' + asset_name + '''/set_switch/input")

if source == 0:
    input = hou.ch("../../../''' + asset_name + '''/set_switch/input")
elif source == 1:
    input = hou.ch("../../../''' + asset_name + '''/shot_switch/input")
else:
    return "''' + str(group) + '''"

if input == 0:
    prefix = "''' + model_name + '''_"
else:
    prefix = "''' + rig_name + '''_"

return prefix + "''' + str(group) + '''"
	'''
	return expression

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
