import hou


def buildRenderCtrls():
	out = hou.node("out")

	renderControls = out.createNode("subnet", node_name="renderControls")

	allMerge = renderControls.createNode("merge", "allMerge")
	defaultMerge = renderControls.createNode("merge", "defualtMerge")
	customMerge = renderControls.createNode("merge", "customMerge")

	allMerge.setInput(0, defaultMerge)
	allMerge.setInput(1, customMerge)

	for i, inputNode in enumerate(renderControls.indirectInputs()):
 		customMerge.setInput(i, inputNode)

	renderControls.layoutChildren()
