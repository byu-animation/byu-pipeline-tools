import hou
import os
# import pyqt_houdini
from PySide2 import QtGui, QtWidgets, QtCore

from byuam import Department, Project, Environment
from byugui.assemble_gui import AssembleWindow

def assemble_hda():
	asset_name = checkout_window.result

	if asset_name is None:
		return

	project = Project()
	environment = Environment()
	username = project.get_current_username()
	asset = project.get_asset(asset_name)

	assembly = asset.get_element(Department.ASSEMBLY)
	checkout_file = assembly.checkout(username)

	element = asset.get_element(Department.MODEL)
	cache = element.get_cache_dir()
	cache = cache.replace(project.get_project_dir(), '$JOB')
	geo_files = [x for x in os.listdir(element.get_cache_dir()) if not os.path.isdir(x)]
	# Remove anything that is not an alembic files
	for file_path in list(geo_files):
		if(not str(file_path).lower().endswith('.abc')):
			geo_files.remove(file_path)

	obj = hou.node('/obj')
	subnet = obj.createNode('subnet')
	shop = subnet.createNode('shopnet', asset_name + '_shopnet')
	for geo_file in geo_files:
		geo_file_path = os.path.join(cache, geo_file)
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
		renderman_folder = hou_parm_template = hou.FolderParmTemplate('stdswitcher4_1', 'RenderMan', folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)

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

		# Code for ri_dbound parm
		hou_parm = geo.parm('ri_rendersubd')
		hou_parm.lock(False)
		hou_parm.set(1)
		hou_parm.setAutoscope(False)

		for child in geo.children():
			child.destroy()
		abc = geo.createNode('alembic')
		abc.parm('fileName').set(geo_file_path)
		convert = abc.createOutputNode('convert')
		convert.setDisplayFlag(True)
		convert.setRenderFlag(True)
		geo.setName(name, unique_name=True)


	subnet.layoutChildren()
	shop.layoutChildren()
	# We problably don't need this anymore now that we are jumping right into digital asset creation.
	subnet.setName(asset_name, unique_name=True)

	# For your convience the variables are labeled as they appear in the create new digital asset dialogue box in Houdini
	# I know at least for me it was dreadfully unclear that the description was going to be the name that showed up in the tab menu.
	# node by saving it to the 'checkout_file' it will put the working copy of the otl in the user folder in the project directory so
	# the working copy won't clutter up their personal otl space.
	operatorName = assembly.get_short_name()
	operatorLabel = (project.get_name() + ' ' + asset_name).title()
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
