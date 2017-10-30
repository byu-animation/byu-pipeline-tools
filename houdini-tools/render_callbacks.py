import hou
from byuam import Project, Department
from byugui import message_gui
import os

def localRender():
	message_gui.info("Local rendering is not yet supported")

def farmRender():
	message_gui.info("Farm render is not yet supported")

def gridmarketsRender():
	message_gui.info("Gridmarkets rendering is not yet supported")

def getShotName():
	project = Project()
	scene = hou.hipFile.name()
	src_dir = os.path.dirname(scene)
	element = project.get_checkout_element(src_dir)
	if element is None:
		print "We are not in a checkouted out element so we can't really render to a folder right now"
		return None
	return element.get_parent()

def get_subdirs(renderDir):
	return [name for name in os.listdir(renderDir) if os.path.isdir(os.path.join(renderDir, name))]

def getVersion(renderDir=None):
	project = Project()
	scene = hou.hipFile.name()
	src_dir = os.path.dirname(scene)
	element = project.get_checkout_element(src_dir)
	parent = element.get_parent()
	shot = project.get_shot(parent)
	renderElement = shot.get_element(Department.RENDER)
	print "This is the parent ", renderElement
	print "This is the parent type ", type(renderElement)
	if element is None:
		print "We are not in a checkouted out element so we can't really render to a folder right now"
		return None
	elemDir = renderElement.get_dir()
	renderDir = renderElement.get_render_dir()

	# Get the sub dir and figure out which is the next version
	subDirs = get_subdirs(elemDir)
	versions = list()
	for subDir in subDirs:
		try:
			versions.append(int(subDir))
		except:
			continue
	if len(versions) == 0:
		return 1
	versions.sort()
	return versions[len(versions) - 1] + 1

def setup():
	subnet = hou.node('out').createNode('subnet', node_name="risNodes")
	subnet.setName("render")
	merge = subnet.createNode('merge', 'risMerge')

def adjustNodes():
	'''
	This will go through my render node and create ris nodes for each layer and properly hook up everting.
	Just in case we loose my node the "as Code" version is down bellow
	'''
	out = hou.node('/out')
	print out
	project = Project()
	renderEngine = hou.node('/out/' + project.get_name() + 'RenderEngine')
	if renderEngine is None:
		renderEngine = out.createNode('subnet', node_name=project.get_name() + 'RenderEngine')
	# Get nodes we need to work with
	merge = hou.node(renderEngine.path() + '/risMerge')
	if merge is None:
		merge = renderEngine.createNode('merge', 'risMerge')
	renderCtrl = hou.pwd()

	# Get the number of layers we should have and the number of layers we actually have
	numLayers = renderCtrl.parm('layers').evalAsInt()
	risNodes = merge.inputAncestors()
	numNodes = len(risNodes)

	# Harmonize layer expectations to reality
	if numLayers < numNodes:
		print 'numLayers: ' + str(numLayers)
		print 'numNodes: ' + str(numNodes)
		for i in range(numNodes - numLayers):
			risNodes[numNodes - (1 + i)].destroy()
	else:
		print 'numLayers: ' + str(numLayers)
		print 'numNodes: ' + str(numNodes)
		for i in range(numLayers - numNodes):
			pos = numNodes + i
			risNode = merge.createInputNode(pos, 'ris')
			chanNum = risNode.name()[3:]

			# Create all of the exporessions
			trange = 'ch("' + renderCtrl.path() + '/trange")'
			risNode.parm('trange').setExpression(trange)
			f1 = 'ch("' + renderCtrl.path() + '/f1")'
			f2 = 'ch("' + renderCtrl.path() + '/f2")'
			f3 = 'ch("' + renderCtrl.path() + '/f3")'
			risNode.parm('f1').setExpression(f1)
			risNode.parm('f2').setExpression(f2)
			risNode.parm('f3').setExpression(f3)
			camera = 'chsop("' + renderCtrl.path() + '/camera")'
			risNode.parm('camera').setExpression(camera)
			ri_device = 'chs("' + renderCtrl.path() + '/ri_device")'
			risNode.parm('ri_device').setExpression(ri_device)

			# Layer specific expressions
			ri_display = 'chs("' + renderCtrl.path() + '/ri_display' + chanNum + '")'
			risNode.parm('ri_display').setExpression(ri_display)

			#Objects
			vobject = 'chsop("' + renderCtrl.path() + '/vobject' + chanNum + '")'
			risNode.parm('vobject').setExpression(vobject)
			forceobject = 'chsop("' + renderCtrl.path() + '/forceobject' + chanNum + '")'
			risNode.parm('forceobject').setExpression(forceobject)
			matte_objects = 'chsop("' + renderCtrl.path() + '/matte_objects' + chanNum + '")'
			risNode.parm('matte_objects').setExpression(matte_objects)
			phantom_objects = 'chsop("' + renderCtrl.path() + '/phantom_objects' + chanNum + '")'
			risNode.parm('phantom_objects').setExpression(phantom_objects)
			excludeobject = 'chsop("' + renderCtrl.path() + '/excludeobject' + chanNum + '")'
			risNode.parm('excludeobject').setExpression(excludeobject)
			#Lights
			sololight = 'chsop("' + renderCtrl.path() + '/sololight' + chanNum + '")'
			risNode.parm('sololight').setExpression(sololight)
			alights = 'chsop("' + renderCtrl.path() + '/alights' + chanNum + '")'
			risNode.parm('alights').setExpression(alights)
			forcelights = 'chsop("' + renderCtrl.path() + '/forcelights' + chanNum + '")'
			risNode.parm('forcelights').setExpression(forcelights)
			excludelights = 'chsop("' + renderCtrl.path() + '/excludelights' + chanNum + '")'
			risNode.parm('excludelights').setExpression(excludelights)
			#Depth of Field
			ri_dof = 'ch("' + renderCtrl.path() + '/ri_dof' + chanNum + '")'
			risNode.parm('ri_dof').setExpression(ri_dof)
			ri_focusregion = 'ch("' + renderCtrl.path() + '/ri_focusregion' + chanNum + '")'
			risNode.parm('ri_focusregion').setExpression(ri_focusregion)
			#Render Driver
			target = 'chs("' + renderCtrl.path() + '/target' + chanNum + '")'
			risNode.parm('target').setExpression(target)
			rib_outputmode = 'ch("' + renderCtrl.path() + '/rib_outputmode' + chanNum + '")'
			risNode.parm('rib_outputmode').setExpression(rib_outputmode)
			soho_diskfile = 'chs("' + renderCtrl.path() + '/soho_diskfile' + chanNum + '")'
			risNode.parm('soho_diskfile').setExpression(soho_diskfile)

	#rename the nodes so that we make sure we have the right names in the right order
	risNodes = merge.inputAncestors()
	for i, risNode in enumerate(risNodes):
		try:
			name = 'temp' + 'ris' + str(i + 1);
			risNode.setName(name)
		except hou.OperationFailed, e:
			print str(e)

	# get rid of temp solution
	for risNode in risNodes:
		risNode.setName(risNode.name()[4:])

	#Set up all expressions for output names
	for i in range(1, numLayers + 1):
		shotName = getShotName()
		if shotName is None:
			rendFilePath = '$JOB/test-renders/'
			versionNum = getVersion(dirPath=rendFilePath)
			rendFilePath = rendFilePath + str(versionNum) + "/"
			ribFilePath = rendFilePath + "rib/"
		else:
			versionNum = getVersion()
			rendFilePath = '$JOB/production/shots/' + shotName + '/render/main/' + str(versionNum) + '/'
			ribFilePath = '$JOB/production/ribs/' + shotName + '/' + str(versionNum) + '/'

		renderCtrl.parm('filename' + str(i)).setExpression('strcat(chs("layername' + str(i) + '"),"$F4")')
		renderCtrl.parm('ri_display' + str(i)).setExpression('strcat(strcat("' + rendFilePath + '",chs("filename' + str(i) + '")),".exr")')
		renderCtrl.parm('soho_diskfile' + str(i)).setExpression('strcat(strcat("' + ribFilePath + '",chs("filename' + str(i) + '")),".exr")')


	renderEngine.layoutChildren()


def createRenderNode():
	print "Test"
	# Initialize parent node variable.
	if locals().get("hou_parent") is None:
		hou_parent = hou.node("/out")

	# Code for /out/tomato
	hou_node = hou_parent.createNode("subnet", "tomato", run_init_scripts=False, load_contents=True, exact_type_name=True)
	hou_node.move(hou.Vector2(-5.83874, 1.52403))
	hou_node.bypass(False)
	hou_node.hide(False)
	hou_node.setLocked(False)
	hou_node.setSelected(False)

	hou_parm_template_group = hou.ParmTemplateGroup()
	# Code for parameter template
	hou_parm_template = hou.ButtonParmTemplate("execute", "Render")
	hou_parm_template.setJoinWithNext(True)
	hou_parm_template.setTags({"takecontrol": "always"})
	hou_parm_template_group.append(hou_parm_template)
	# Code for parameter template
	hou_parm_template = hou.ButtonParmTemplate("renderdialog", "Controls...")
	hou_parm_template.setTags({"takecontrol": "always"})
	hou_parm_template_group.append(hou_parm_template)
	# Code for parameter template
	hou_parm_template = hou.MenuParmTemplate("trange", "Valid Frame Range", menu_items=(["off","normal","on"]), menu_labels=(["Render Current Frame","Render Frame Range","Render Frame Range Only (Strict)"]), default_value=0, icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template.setTags({"autoscope": "0000000000000000"})
	hou_parm_template_group.append(hou_parm_template)
	# Code for parameter template
	hou_parm_template = hou.FloatParmTemplate("f", "Start/End/Inc", 3, default_value=([0, 0, 1]), default_expression=(["$FSTART","$FEND",""]), default_expression_language=([hou.scriptLanguage.Hscript,hou.scriptLanguage.Hscript,hou.scriptLanguage.Hscript]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
	hou_parm_template.setConditional( hou.parmCondType.DisableWhen, "{ framerangedisable == 0 }")
	hou_parm_template.setTags({"autoscope": "0000000000000000"})
	hou_parm_template_group.append(hou_parm_template)
	# Code for parameter template
	hou_parm_template = hou.StringParmTemplate("camera", "Camera", 1, default_value=(["/obj/cam1"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template.setTags({"autoscope": "0000000000000000", "opfilter": "!!OBJ/CAMERA!!", "oprelative": "."})
	hou_parm_template_group.append(hou_parm_template)
	# Code for parameter template
	hou_parm_template = hou.StringParmTemplate("ri_device", "Display Device", 1, default_value=(["houdini"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["framebuffer","x11","windows","tiff","sgif","alias","targa","cineon","softimage","mayaiff","shadow","zfile","openexr","texture","houdini"]), menu_labels=(["Framebuffer Device","X11 Display","Windows Display","TIFF File","SGI Image","Alias Image","Targa","Cineon","Soft Image","Maya IFF","Shadow Device","Z-File Device","Open EXR","Texture File","Houdini Display"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.StringReplace)
	hou_parm_template.setHelp("RiDisplay (type)")
	hou_parm_template.setTags({"autoscope": "0000000000000000", "spare_category": "Display"})
	hou_parm_template_group.append(hou_parm_template)
	# Code for parameter template
	hou_parm_template = hou.IntParmTemplate("framerangedisable", "Disable Frame Range", 1, default_value=([0]), default_expression=(["ch(\"trange\")"]), default_expression_language=([hou.scriptLanguage.Hscript]), min=0, max=10, min_is_strict=False, max_is_strict=False, naming_scheme=hou.parmNamingScheme.Base1, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template.hide(True)
	hou_parm_template_group.append(hou_parm_template)
	# Code for parameter template
	hou_parm_template = hou.FolderParmTemplate("layers", "Layers", folder_type=hou.folderType.MultiparmBlock, default_value=0, ends_tab_group=False)
	hou_parm_template.setScriptCallback("import render_callbacks; render_callbacks.adjustNodes()")
	hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
	hou_parm_template.setTags({"script_callback": "import render_callbacks; render_callbacks.adjustNodes()", "script_callback_language": "python"})
	# Code for parameter template
	hou_parm_template2 = hou.FolderParmTemplate("layerinfo#", "Layer Info", folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("layername#", "Layer Name", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("filename#", "File Name", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("ri_display#", "Display", 1, default_value=(["$HIP/render/$HIPNAME.$OS.$F4.exr"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.FileReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="opmenu -l ris1 ri_display", item_generator_script_language=hou.scriptLanguage.Hscript, menu_type=hou.menuType.StringReplace)
	hou_parm_template3.setHelp("RiDisplay (name)")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "filechooser_mode": "write", "spare_category": "Display"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("notes#", "Notes", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template3.setTags({"editor": "1"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	hou_parm_template.addParmTemplate(hou_parm_template2)
	# Code for parameter template
	hou_parm_template2 = hou.FolderParmTemplate("layerinfo#_1", "Objects", folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("vobject#", "Candidate Objects", 1, default_value=(["*"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReferenceList, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template3.setHelp("Objects will not be output if their display flag is off")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "opfilter": "!!OBJ/GEOMETRY!!", "oprelative": "/obj"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("forceobject#", "Force Objects", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReferenceList, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template3.setHelp("Objects will be output regardless of the state of their display flag")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "opfilter": "!!OBJ/GEOMETRY!!", "oprelative": "/obj"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("matte_objects#", "Forced Matte", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReferenceList, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template3.setHelp("Objects forced to be output as matte objects")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "opfilter": "!!OBJ/GEOMETRY!!", "oprelative": "/obj"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("phantom_objects#", "Forced Phantom", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReferenceList, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template3.setHelp("Objects forced to be output as having no camera visibility")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "opfilter": "!!OBJ/GEOMETRY!!", "oprelative": "/obj"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("excludeobject#", "Exclude Objects", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReferenceList, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template3.setHelp("Objects which are not output")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "opfilter": "!!OBJ/GEOMETRY!!", "oprelative": "/obj"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.SeparatorParmTemplate("sepparm#")
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("sololight#", "Solo Light", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReferenceList, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template3.setHelp("Solo Lights")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "opfilter": "!!OBJ/LIGHT!!", "oprelative": "/obj"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("alights#", "Candidate Lights", 1, default_value=(["*"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReferenceList, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template3.setConditional( hou.parmCondType.DisableWhen, "{ sololight != \\\"\\\" }")
	hou_parm_template3.setHelp("Lights will not be output if their dimmer channel is 0.")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "opfilter": "!!OBJ/LIGHT!!", "oprelative": "/obj"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("forcelights#", "Force Lights", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReferenceList, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template3.setConditional( hou.parmCondType.DisableWhen, "{ sololight != \\\"\\\" }")
	hou_parm_template3.setHelp("Lights will be output regardless of the value of their dimmer channel")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "opfilter": "!!OBJ/LIGHT!!", "oprelative": "/obj"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("excludelights#", "Exclude Lights", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReferenceList, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	hou_parm_template3.setConditional( hou.parmCondType.DisableWhen, "{ sololight != \\\"\\\" }")
	hou_parm_template3.setHelp("Lights will not be output under any circumstances.")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "opfilter": "!!OBJ/LIGHT!!", "oprelative": "/obj"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	hou_parm_template.addParmTemplate(hou_parm_template2)
	# Code for parameter template
	hou_parm_template2 = hou.FolderParmTemplate("layerinfo#_2", "Depth Of Field", folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
	# Code for parameter template
	hou_parm_template3 = hou.ToggleParmTemplate("ri_dof#", "Enable Depth Of Field", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "spare_category": "Depth Of Field"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.FloatParmTemplate("ri_focusregion#", "Focus Region", 1, default_value=([0]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
	hou_parm_template3.setConditional( hou.parmCondType.DisableWhen, "{ ri_dof# == 0 }")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "spare_category": "Depth Of Field"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	hou_parm_template.addParmTemplate(hou_parm_template2)
	# Code for parameter template
	hou_parm_template2 = hou.FolderParmTemplate("layerinfo#_3", "Driver", folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("target#", "Render Target", 1, default_value=(["prman21.0"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="opmenu -l ris1 target", item_generator_script_language=hou.scriptLanguage.Hscript, menu_type=hou.menuType.Normal)
	hou_parm_template3.setTags({"autoscope": "0000000000000000"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.ToggleParmTemplate("rib_outputmode#", "Save RIB File To Disk", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
	hou_parm_template3.hideLabel(True)
	hou_parm_template3.setJoinWithNext(True)
	hou_parm_template3.setTags({"autoscope": "0000000000000000"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	# Code for parameter template
	hou_parm_template3 = hou.StringParmTemplate("soho_diskfile#", "Disk File", 1, default_value=(["$HIP/houdini.rib"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.FileReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="opmenu -l ris1 soho_diskfile", item_generator_script_language=hou.scriptLanguage.Hscript, menu_type=hou.menuType.StringReplace)
	hou_parm_template3.setConditional( hou.parmCondType.DisableWhen, "{ rib_outputmode# == 0 }")
	hou_parm_template3.setTags({"autoscope": "0000000000000000", "filechooser_mode": "write"})
	hou_parm_template2.addParmTemplate(hou_parm_template3)
	hou_parm_template.addParmTemplate(hou_parm_template2)
	hou_parm_template_group.append(hou_parm_template)
	hou_node.setParmTemplateGroup(hou_parm_template_group)
	# Code for /out/tomato/execute parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("execute")
	hou_parm.lock(False)
	hou_parm.set("0")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/renderdialog parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("renderdialog")
	hou_parm.lock(False)
	hou_parm.set("0")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/trange parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("trange")
	hou_parm.lock(False)
	hou_parm.set("off")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/f parm tuple
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm_tuple = hou_node.parmTuple("f")
	hou_parm_tuple.lock((False, False, False))
	hou_parm_tuple.set((1, 240, 1))
	hou_parm_tuple.setAutoscope((False, False, False))

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.Keyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setValue(0)
	hou_keyframe.useValue(False)
	hou_keyframe.setSlope(0)
	hou_keyframe.useSlope(False)
	hou_keyframe.setAccel(0)
	hou_keyframe.useAccel(False)
	hou_keyframe.setExpression("$FSTART", hou.exprLanguage.Hscript)
	hou_parm_tuple[0].setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.Keyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setValue(0)
	hou_keyframe.useValue(False)
	hou_keyframe.setSlope(0)
	hou_keyframe.useSlope(False)
	hou_keyframe.setAccel(0)
	hou_keyframe.useAccel(False)
	hou_keyframe.setExpression("$FSTART", hou.exprLanguage.Hscript)
	hou_parm_tuple[0].setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.Keyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setValue(0)
	hou_keyframe.useValue(False)
	hou_keyframe.setSlope(0)
	hou_keyframe.useSlope(False)
	hou_keyframe.setAccel(0)
	hou_keyframe.useAccel(False)
	hou_keyframe.setExpression("$FSTART", hou.exprLanguage.Hscript)
	hou_parm_tuple[0].setKeyframe(hou_keyframe)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.Keyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setValue(0)
	hou_keyframe.useValue(False)
	hou_keyframe.setSlope(0)
	hou_keyframe.useSlope(False)
	hou_keyframe.setAccel(0)
	hou_keyframe.useAccel(False)
	hou_keyframe.setExpression("$FEND", hou.exprLanguage.Hscript)
	hou_parm_tuple[1].setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.Keyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setValue(0)
	hou_keyframe.useValue(False)
	hou_keyframe.setSlope(0)
	hou_keyframe.useSlope(False)
	hou_keyframe.setAccel(0)
	hou_keyframe.useAccel(False)
	hou_keyframe.setExpression("$FEND", hou.exprLanguage.Hscript)
	hou_parm_tuple[1].setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.Keyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setValue(0)
	hou_keyframe.useValue(False)
	hou_keyframe.setSlope(0)
	hou_keyframe.useSlope(False)
	hou_keyframe.setAccel(0)
	hou_keyframe.useAccel(False)
	hou_keyframe.setExpression("$FEND", hou.exprLanguage.Hscript)
	hou_parm_tuple[1].setKeyframe(hou_keyframe)


	# Code for /out/tomato/camera parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("camera")
	hou_parm.lock(False)
	hou_parm.set("/obj/cam1")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/ri_device parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("ri_device")
	hou_parm.lock(False)
	hou_parm.set("houdini")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/framerangedisable parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("framerangedisable")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.Keyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setValue(0)
	hou_keyframe.useValue(False)
	hou_keyframe.setSlope(0)
	hou_keyframe.useSlope(False)
	hou_keyframe.setAccel(0)
	hou_keyframe.useAccel(False)
	hou_keyframe.setExpression("ch(\"trange\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.Keyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setValue(0)
	hou_keyframe.useValue(False)
	hou_keyframe.setSlope(0)
	hou_keyframe.useSlope(False)
	hou_keyframe.setAccel(0)
	hou_keyframe.useAccel(False)
	hou_keyframe.setExpression("ch(\"trange\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.Keyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setValue(0)
	hou_keyframe.useValue(False)
	hou_keyframe.setSlope(0)
	hou_keyframe.useSlope(False)
	hou_keyframe.setAccel(0)
	hou_keyframe.useAccel(False)
	hou_keyframe.setExpression("ch(\"trange\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.Keyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setValue(0)
	hou_keyframe.useValue(False)
	hou_keyframe.setSlope(0)
	hou_keyframe.useSlope(False)
	hou_keyframe.setAccel(0)
	hou_keyframe.useAccel(False)
	hou_keyframe.setExpression("ch(\"trange\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)


	# Code for /out/tomato/layers parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("layers")
	hou_parm.lock(False)
	hou_parm.set(3)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/layerinfo11 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("layerinfo11")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/layername1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("layername1")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/filename1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("filename1")
	hou_parm.lock(False)
	hou_parm.set("$F4")
	hou_parm.setAutoscope(True)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername1\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername1\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername1\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername1\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)


	# Code for /out/tomato/ri_display1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("ri_display1")
	hou_parm.lock(False)
	hou_parm.set("$JOB/production/shots/a001/render/main/1/$F4.exr")
	hou_parm.setAutoscope(True)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename1\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename1\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename1\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename1\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)


	# Code for /out/tomato/notes1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("notes1")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/vobject1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("vobject1")
	hou_parm.lock(False)
	hou_parm.set("*")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/forceobject1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("forceobject1")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/matte_objects1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("matte_objects1")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/phantom_objects1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("phantom_objects1")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/excludeobject1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("excludeobject1")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/sololight1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("sololight1")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/alights1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("alights1")
	hou_parm.lock(False)
	hou_parm.set("*")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/forcelights1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("forcelights1")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/excludelights1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("excludelights1")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/ri_dof1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("ri_dof1")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/ri_focusregion1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("ri_focusregion1")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/target1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("target1")
	hou_parm.lock(False)
	hou_parm.set("prman21.0")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/rib_outputmode1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("rib_outputmode1")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/soho_diskfile1 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("soho_diskfile1")
	hou_parm.lock(False)
	hou_parm.set("$JOB/production/ribs/a001/1/$F4.exr")
	hou_parm.setAutoscope(True)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename1\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename1\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename1\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename1\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)


	# Code for /out/tomato/layerinfo21 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("layerinfo21")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/layername2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("layername2")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/filename2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("filename2")
	hou_parm.lock(False)
	hou_parm.set("$F4")
	hou_parm.setAutoscope(True)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername2\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername2\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername2\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername2\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)


	# Code for /out/tomato/ri_display2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("ri_display2")
	hou_parm.lock(False)
	hou_parm.set("$JOB/production/shots/a001/render/main/1/$F4.exr")
	hou_parm.setAutoscope(True)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename2\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename2\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename2\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename2\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)


	# Code for /out/tomato/notes2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("notes2")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/vobject2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("vobject2")
	hou_parm.lock(False)
	hou_parm.set("*")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/forceobject2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("forceobject2")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/matte_objects2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("matte_objects2")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/phantom_objects2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("phantom_objects2")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/excludeobject2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("excludeobject2")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/sololight2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("sololight2")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/alights2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("alights2")
	hou_parm.lock(False)
	hou_parm.set("*")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/forcelights2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("forcelights2")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/excludelights2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("excludelights2")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/ri_dof2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("ri_dof2")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/ri_focusregion2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("ri_focusregion2")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/target2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("target2")
	hou_parm.lock(False)
	hou_parm.set("prman21.0")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/rib_outputmode2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("rib_outputmode2")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/soho_diskfile2 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("soho_diskfile2")
	hou_parm.lock(False)
	hou_parm.set("$JOB/production/ribs/a001/1/$F4.exr")
	hou_parm.setAutoscope(True)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename2\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename2\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename2\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename2\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)


	# Code for /out/tomato/layerinfo31 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("layerinfo31")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/layername3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("layername3")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/filename3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("filename3")
	hou_parm.lock(False)
	hou_parm.set("$F4")
	hou_parm.setAutoscope(True)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername3\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername3\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername3\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(chs(\"layername3\"),\"$F4\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)


	# Code for /out/tomato/ri_display3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("ri_display3")
	hou_parm.lock(False)
	hou_parm.set("$JOB/production/shots/a001/render/main/1/$F4.exr")
	hou_parm.setAutoscope(True)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename3\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename3\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename3\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/shots/a001/render/main/1/\",chs(\"filename3\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)


	# Code for /out/tomato/notes3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("notes3")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/vobject3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("vobject3")
	hou_parm.lock(False)
	hou_parm.set("*")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/forceobject3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("forceobject3")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/matte_objects3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("matte_objects3")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/phantom_objects3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("phantom_objects3")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/excludeobject3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("excludeobject3")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/sololight3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("sololight3")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/alights3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("alights3")
	hou_parm.lock(False)
	hou_parm.set("*")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/forcelights3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("forcelights3")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/excludelights3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("excludelights3")
	hou_parm.lock(False)
	hou_parm.set("")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/ri_dof3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("ri_dof3")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/ri_focusregion3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("ri_focusregion3")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/target3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("target3")
	hou_parm.lock(False)
	hou_parm.set("prman21.0")
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/rib_outputmode3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("rib_outputmode3")
	hou_parm.lock(False)
	hou_parm.set(0)
	hou_parm.setAutoscope(False)


	# Code for /out/tomato/soho_diskfile3 parm
	if locals().get("hou_node") is None:
		hou_node = hou.node("/out/tomato")
	hou_parm = hou_node.parm("soho_diskfile3")
	hou_parm.lock(False)
	hou_parm.set("$JOB/production/ribs/a001/1/$F4.exr")
	hou_parm.setAutoscope(True)

	# Code for first keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename3\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for last keyframe.
	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename3\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename3\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)

	# Code for keyframe.
	hou_keyframe = hou.StringKeyframe()
	hou_keyframe.setTime(0)
	hou_keyframe.setExpression("strcat(strcat(\"$JOB/production/ribs/a001/1/\",chs(\"filename3\")),\".exr\")", hou.exprLanguage.Hscript)
	hou_parm.setKeyframe(hou_keyframe)


	hou_node.setColor(hou.Color([0.8, 0.8, 0.8]))
	hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

	# hou_node.setUserData("___Version___", "16.0.504.20")
	# if hasattr(hou_node, "syncNodeVersionIfNeeded"):
	# hou_node.syncNodeVersionIfNeeded("16.0.504.20")
