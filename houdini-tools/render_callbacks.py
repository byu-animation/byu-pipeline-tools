import hou
from byuam import Project, Department
from byugui import message_gui
import tractor_submit as tractor
import os



def prepRender(rib=False, openExr=False):
	'''
	Prepares the render. Return True if the render is ready to go. Otherwise false
	'''
	nodes = getEngineParts()
	# set render quality
	quality = nodes['renderCtrl'].parm('renderquality').evalAsString()
	setRenderQuality(quality=quality)
	#Make sure layers all up-to-date
	adjustNodes() #TODO We need to make sure that we have updated the version number of the render before we render. Right now it only updates when a layer is added. I think the adjust Nodes function should do that for us. Lets make sure before we get rid of this TODO
	#Make sure we aren't outputing rib files
	setRibOutputMode(rib)
	#Make sure that all of the layers have names
	numLayers = nodes['renderCtrl'].parm('layers').evalAsInt()
	if numLayers < 1:
		message_gui.error('Make sure you have at least one layer.')
		return False
	missingNames = []
	for i in range(1, numLayers + 1):
		layerName = nodes['renderCtrl'].parm('layername' + str(i)).eval()
		if layerName == '':
			missingNames.append(i)
		print layerName
	if len(missingNames) != 0:
		message_gui.error('Make sure that you have named all of the layers.', details=layerListToString(missingNames))
		return False
	#Make sure we are using the correnct display device
	device = nodes['renderCtrl'].parm('ri_device').eval()
	if openExr and device != 'openexr':
		message_gui.error('Make sure that the display device is set to "openexr" before sending a job to Tractor.')
		return False
	return True

def layerListToString(nums):
	if len(nums) == 1:
		return 'Layer ' + str(nums[0]) + ' doesn\'t have a name.'
	else:
		missingNames = ''
		for num in nums:
			missingNames += str(num) + ','
		missingNames = missingNames[0:len(missingNames) - 2] + ' and ' + missingNames[len(missingNames)-2]
		return 'Layers ' + missingNames + ' don\'t have names.'

def localRender():
	if prepRender():
		print 'Start Local Render'
		try:
			getEngineParts()['merge'].render()
		except hou.OperationFailed, e:
			message_gui.error('There was an error completeing the render. Check the ris nodes in the render engine node for details.', details=str(e))

def farmRender():
	if prepRender(rib=True, openExr=True):
		print 'Start Tractor Render'
		try:
			tractor.go(getEngineParts()['merge'].inputAncestors())
		except hou.OperationFailed, e:
			message_gui.error('There was an error completeing the render. Check the ris nodes in the render engine node for details.', details=str(e))

def gridmarketsRender():
	if prepRender(openExr=True):
		print 'Start Gridmarkets Render'
		try:
			getEngineParts()['gridmarkets'].parm('submit_start').pressButton()
		except hou.OperationFailed, e:
			message_gui.error('There was an error completeing the render. Check the ris nodes in the render engine node for details.', details=str(e))

def firstMiddleLast():
	if prepRender():
		print 'Start FML Render'
		nodes = getEngineParts()
		firstFrame = nodes['renderCtrl'].parm('f1').eval()
		lastFrame = nodes['renderCtrl'].parm('f2').eval()
		middleFrame = firstFrame + ((lastFrame - firstFrame)/2)

		print 'first: ', firstFrame
		print 'last: ', lastFrame
		print 'middle: ', middleFrame

		setRenderQuality(quality='final')

		try:
			nodes['merge'].render([firstFrame, firstFrame])
			nodes['merge'].render([middleFrame, middleFrame])
			nodes['merge'].render([lastFrame, lastFrame])
		except hou.OperationFailed, e:
			message_gui.error('There was an error completeing the render. Check the ris nodes in the render engine node for details.', details=str(e))

def setRenderQuality(quality='default', minSamples=-1, maxSamples=64):
	if quality == 'final':
		minSamples = 600
		maxSamples = 1000
	elif quality == 'dailies':
		minSamples = 300
		maxSamples = 700

	node = getEngineParts()['renderCtrl']

	for i in range(1, node.parm('layers').evalAsInt() + 1):
		if quality == 'custom':
			minSamples = node.parm('custom_minsamples' + str(i)).evalAsInt()
			maxSamples = node.parm('custom_maxsamples' + str(i)).evalAsInt()
		parmName = 'ri_minsamples' + str(i)
		node.parm('ri_minsamples' + str(i)).set(minSamples)
		node.parm('ri_maxsamples' + str(i)).set(maxSamples)


def setRibOutputMode(state):
	nodes = getEngineParts()
	risNodes = nodes['merge'].inputAncestors()
	for risNode in risNodes:
		risNode.parm('rib_outputmode').set(state)

def getShotName():
	project = Project()
	scene = hou.hipFile.name()
	src_dir = os.path.dirname(scene)
	element = project.get_checkout_element(src_dir)
	if element is None:
		return None
	return element.get_parent()

def get_subdirs(renderDir):
	return [name for name in os.listdir(renderDir) if os.path.isdir(os.path.join(renderDir, name))]

def getVersion(renderDir=None):
	if renderDir is None:
		project = Project()
		scene = hou.hipFile.name()
		src_dir = os.path.dirname(scene)
		element = project.get_checkout_element(src_dir)
		if element is None:
			return None
		parent = element.get_parent()
		shot = project.get_shot(parent)
		renderElement = shot.get_element(Department.RENDER)
		renderDir = renderElement.get_dir()

	# Get the sub dir and figure out which is the next version
	subDirs = get_subdirs(renderDir)
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
	subnet = hou.node('out').createNode('subnet', node_name='risNodes')
	subnet.setName('render')
	merge = subnet.createNode('merge', 'risMerge')

def getEngineParts():
	project = Project()
	nodes = {}
	nodes['out'] = hou.node('/out')
	nodes['renderCtrl'] = hou.pwd()

	nodes['renderEngine'] = nodes['renderCtrl'].parent().node(project.get_name() + 'RenderEngine')
	if nodes['renderEngine'] is None:
		nodes['renderEngine'] = nodes['renderCtrl'].parent().createNode('subnet', node_name=project.get_name() + 'RenderEngine')

	nodes['merge'] = nodes['renderEngine'].node('risMerge')
	if nodes['merge'] is None:
		nodes['merge'] = nodes['renderEngine'].createNode('merge', 'risMerge')

	nodes['gridmarkets'] = nodes['renderEngine'].node('GridMarketsSubmit')
	if nodes['gridmarkets'] is None:
		nodes['gridmarkets'] = nodes['merge'].createOutputNode('render_submit', 'GridMarketsSubmit')
	return nodes

def setParmExp(destNode, srcNode, parmName, layerNum='', channelType='ch', size=1, useXYZ=False, useRGB=False):
	for i in range(1, size + 1):
		if useXYZ:
			if i is 1:
				index = 'x'
			elif i is 2:
				index = 'y'
			elif i is 3:
				index = 'z'
		elif useRGB:
			if i is 1:
				index = 'r'
			elif i is 2:
				index = 'g'
			elif i is 3:
				index = 'b'
		else:
			index = i
		parmNamewithLayer = parmName + str(layerNum) + (str(index) if size > 1 else '')
		expressionString = channelType + '("' + srcNode.path() + '/' + parmNamewithLayer + '")'
		parmNameWithSize = parmName + (str(index) if size > 1 else '')
		destNode.parm(parmNameWithSize).setExpression(expressionString)

def addExtraParms(risNode):
	parmGroup = risNode.parmTemplateGroup()

	#Parms for smooth curve rendering for fur
	parmTemplate = hou.StringParmTemplate("ri_curveinterpolation", "Curve Interpolation", 1, default_value=(["linear"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["linear","cubic"]), menu_labels=(["Linear","Cubic"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	parmTemplate.setHelp("RiCurves (type)")
	parmTemplate.setTags({"spare_category": "Geometry"})
	parmGroup.append(parmTemplate)
	parmTemplate = hou.StringParmTemplate("ri_curvebasis", "Curve Basis", 1, default_value=(["bezier"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["bezier","b-spline","catmull-rom","hermite","power"]), menu_labels=(["Bezier","B-Spline","Catmull-Rom","Hermite","Power"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
	parmTemplate.setConditional( hou.parmCondType.DisableWhen, "{ ri_curveinterpolation == linear }")
	parmTemplate.setHelp("RiBasis (basis)")
	parmTemplate.setTags({"spare_category": "Geometry"})
	parmGroup.append(parmTemplate)

	risNode.setParmTemplateGroup(parmGroup)
	return risNode

def setGlobalCtrls(renderCtrl, risNode):
	setParmExp(risNode, renderCtrl, 'trange')
	setParmExp(risNode, renderCtrl, 'f1')
	setParmExp(risNode, renderCtrl, 'f2')
	setParmExp(risNode, renderCtrl, 'f3')
	setParmExp(risNode, renderCtrl, 'camera', channelType='chsop')
	setParmExp(risNode, renderCtrl, 'override_camerares')
	setParmExp(risNode, renderCtrl, 'res_fraction', channelType='chs')
	setParmExp(risNode, renderCtrl, 'res_overridex')
	setParmExp(risNode, renderCtrl, 'res_overridey')
	setParmExp(risNode, renderCtrl, 'ri_device', channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_curveinterpolation', channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_curvebasis', channelType='chs')

def setLayers(renderCtrl, risNode, layerNum):
	# Layer specific expressions
	overrideOutput = renderCtrl.parm('overrideoutput' + layerNum).eval()
	if overrideOutput == 0:
		setParmExp(risNode, renderCtrl, 'ri_display', layerNum=layerNum, channelType='chs')

	viewimg = 'ch' #TODO get this view button to press the other view button

	setObjects(renderCtrl, risNode, layerNum)
	setProperties(renderCtrl, risNode, layerNum)
	setAdvanced(renderCtrl, risNode, layerNum)
	setNotes(renderCtrl, risNode, layerNum)

def setObjects(renderCtrl, risNode, layerNum):
	#Objects
	setParmExp(risNode, renderCtrl, 'vobject', layerNum=layerNum, channelType='chsop')
	setParmExp(risNode, renderCtrl, 'forceobject', layerNum=layerNum, channelType='chsop')
	setParmExp(risNode, renderCtrl, 'matte_objects', layerNum=layerNum, channelType='chsop')
	setParmExp(risNode, renderCtrl, 'phantom_objects', layerNum=layerNum, channelType='chsop')
	setParmExp(risNode, renderCtrl, 'excludeobject', layerNum=layerNum, channelType='chsop')

	#Lights
	setParmExp(risNode, renderCtrl, 'sololight', layerNum=layerNum, channelType='chsop')
	setParmExp(risNode, renderCtrl, 'alights', layerNum=layerNum, channelType='chsop')
	setParmExp(risNode, renderCtrl, 'forcelights', layerNum=layerNum, channelType='chsop')
	setParmExp(risNode, renderCtrl, 'excludelights', layerNum=layerNum, channelType='chsop')

def setProperties(renderCtrl, risNode, layerNum):
	setRIS(renderCtrl, risNode, layerNum)
	setDisplay(renderCtrl, risNode, layerNum)
	setRiAOV(renderCtrl, risNode, layerNum)
	setHider(renderCtrl, risNode, layerNum)
	setRender(renderCtrl, risNode, layerNum)
	setAttributes(renderCtrl, risNode, layerNum)

def setRIS(renderCtrl, risNode, layerNum):
	#RIS
	setParmExp(risNode, renderCtrl, 'shop_integratorpath', layerNum=layerNum, channelType='chsop')
	setParmExp(risNode, renderCtrl, 'ri_pixelvariance', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'soho_denoisemode', layerNum=layerNum)

def setDisplay(renderCtrl, risNode, layerNum):
	#Display
	setParmExp(risNode, renderCtrl, 'ri_channels', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_quantize', layerNum=layerNum, size=4)
	setParmExp(risNode, renderCtrl, 'ri_pixelfilter', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_pixelfilterwidth', layerNum=layerNum, size=2, useXYZ=True)
	setParmExp(risNode, renderCtrl, 'ri_gamma', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_gain', layerNum=layerNum)

def setRiAOV(renderCtrl, risNode, layerNum):
	#TODO RiAOV is going to be tricky. Lets come back to it.
	return None

def setHider(renderCtrl, risNode, layerNum):
	#Hider
	setParmExp(risNode, renderCtrl, 'ri_hider', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_minsamples', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_maxsamples', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_darkfalloff', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_incremental', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_pixelfiltermode', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_aperture', layerNum=layerNum, size=4)
	setParmExp(risNode, renderCtrl, 'ri_samplemotion', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_extrememotiondof', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_dofaspect', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_adaptall', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_pixelsamples', layerNum=layerNum, size=2, useXYZ=True)

def setRender(renderCtrl, risNode, layerNum):
	setParmExp(risNode, renderCtrl, 'render_viewcamera', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'render_any_envmap', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_autobias', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_tracebias', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_tracedisplace', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_texturegaussian', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_texturelerp', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_bucketsize', layerNum=layerNum, size=2, useXYZ=True)

def setAttributes(renderCtrl, risNode, layerNum):
	setParmExp(risNode, renderCtrl, 'ri_visibletransmission', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_indirect', layerNum=layerNum)

def setAdvanced(renderCtrl, risNode, layerNum):
	setDicing(renderCtrl, risNode, layerNum)
	setDriver(renderCtrl, risNode, layerNum)
	setScripts(renderCtrl, risNode, layerNum)
	setStatistics(renderCtrl, risNode, layerNum)
	setNotHookedUp(renderCtrl, risNode, layerNum)
	setLimits(renderCtrl, risNode, layerNum)

def setDicing(renderCtrl, risNode, layerNum):
	setParmExp(risNode, renderCtrl, 'ri_micropolygonlength', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_relativemicropolygonlength', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_resetrelativemicropolygonlength', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_watertight', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_dicepretessellate', layerNum=layerNum)

def setDriver(renderCtrl, risNode, layerNum):
	#Render Driver
	setParmExp(risNode, renderCtrl, 'target', layerNum=layerNum, channelType='chs')
	overrideRib = renderCtrl.parm('overriderib' + layerNum).eval()
	setParmExp(risNode, renderCtrl, 'rib_outputmode', layerNum=layerNum)
	if overrideRib == 0:
		setParmExp(risNode, renderCtrl, 'soho_diskfile', layerNum=layerNum, channelType='chs')

def setScripts(renderCtrl, risNode, layerNum):
	setParmExp(risNode, renderCtrl, 'tprerender', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'prerender', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'lprerender', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'tpreframe', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'preframe', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'lpreframe', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'tpostframe', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'postframe', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'lpostframe', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'tpostrender', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'postrender', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'lpostrender', layerNum=layerNum, channelType='chs')

def setStatistics(renderCtrl, risNode, layerNum):
	setParmExp(risNode, renderCtrl, 'ri_statistics', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_statxmlfilename', layerNum=layerNum)

def setNotHookedUp(renderCtrl, risNode, layerNum):
	setMotionBlur(renderCtrl, risNode, layerNum)
	setDepthOfField(renderCtrl, risNode, layerNum)
	setPath(renderCtrl, risNode, layerNum)
	setLPE(renderCtrl, risNode, layerNum)

def setMotionBlur(renderCtrl, risNode, layerNum):
	setParmExp(risNode, renderCtrl, 'allowmotionblur', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_shutteropening', layerNum=layerNum, size=2)
	setParmExp(risNode, renderCtrl, 'xform_motionsamples', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'geo_motionsamples', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'shutteroffset', layerNum=layerNum)

def setDepthOfField(renderCtrl, risNode, layerNum):
	setParmExp(risNode, renderCtrl, 'ri_dof', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_focusregion', layerNum=layerNum)

def setPath(renderCtrl, risNode, layerNum):
	setParmExp(risNode, renderCtrl, 'ri_rixplugin', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_shaderpath', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_texturepath', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_proceduralpath', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_dirmap', layerNum=layerNum, channelType='chs')

def setLPE(renderCtrl, risNode, layerNum):
	setParmExp(risNode, renderCtrl, 'ri_diffuse2', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_diffuse3', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_specular2', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_specular3', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_specular4', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_specular5', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_specular6', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_specular7', layerNum=layerNum, channelType='chs')
	setParmExp(risNode, renderCtrl, 'ri_specular8', layerNum=layerNum, channelType='chs')

def setLimits(renderCtrl, risNode, layerNum):
	setParmExp(risNode, renderCtrl, 'ri_texturememory', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_opacitycachememory', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_geocachememory', layerNum=layerNum)
	setParmExp(risNode, renderCtrl, 'ri_othreshold', layerNum=layerNum, size=3, useRGB=True)
	setParmExp(risNode, renderCtrl, 'ri_zthreshold', layerNum=layerNum, size=3, useRGB=True)

def setNotes(renderCtrl, risNode, layerNum):
	#So far there is nothing in notes that needs to be spread to the RIS Nodes
	# setParmExp(risNode, renderCtrl, '', layerNum=layerNum)
	return None

def adjustNodes():
	'''
	This will go through my render node and create ris nodes for each layer and properly hook up everting.
	Just in case we loose my node the 'as Code' version is down bellow
	'''
	nodes = getEngineParts()
	renderCtrl = nodes['renderCtrl']
	renderEngine = nodes['renderEngine']
	merge = nodes['merge']

	# Get the number of layers we should have and the number of layers we actually have
	numLayers = renderCtrl.parm('layers').evalAsInt()
	risNodes = merge.inputAncestors()
	numNodes = len(risNodes)

	# Harmonize layer expectations to reality
	if numLayers < numNodes:
		for i in range(numNodes - numLayers):
			risNodes[numNodes - (1 + i)].destroy()
	else:
		for i in range(numLayers - numNodes):
			pos = numNodes + i
			risNode = merge.createInputNode(pos, 'ris')
			addExtraParms(risNode)
			layerNum = risNode.name()[3:]

			# Create all of the exporessions
			setGlobalCtrls(renderCtrl, risNode)
			setLayers(renderCtrl, risNode, layerNum)

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
			renderFilePath = os.path.join(os.environ['JOB'], 'production', 'test-renders')
			if not os.path.exists(renderFilePath):
				os.makedirs(renderFilePath)
			versionNum = getVersion(renderDir=renderFilePath)
			renderFilePath = os.path.join(renderFilePath, str(versionNum))
			ribFilePath = os.path.join(renderFilePath, 'rib')
		else:
			versionNum = getVersion()
			renderFilePath = os.path.join(os.environ['JOB'], 'production', 'shots', str(shotName), 'render', 'main', str(versionNum))
			ribFilePath = os.path.join(os.environ['JOB'], 'production','ribs', shotName, str(versionNum))

		renderCtrl.parm('filename' + str(i)).setExpression('strcat(chs("layername' + str(i) + '"),".$F4")')
		renderCtrl.parm('ri_display' + str(i)).setExpression('strcat(strcat("' + renderFilePath + '/",chs("filename' + str(i) + '")),".exr")')
		renderCtrl.parm('soho_diskfile' + str(i)).setExpression('strcat(strcat("' + ribFilePath + '/",chs("filename' + str(i) + '")),".rib")')


	renderEngine.layoutChildren()
