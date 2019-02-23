import os
from string import Template
from byuam import Project
from byuam import Body



baseXML='''<?xml version="1.0" encoding="UTF-8"?>
<shelfDocument>

    <tool name=\'$NAME\' label=\'$LABEL\' icon=\'$ICON\'>
        <toolMenuContext name=\"network\">
            <contextNetType>$CONTEXT</contextNetType>
        </toolMenuContext>

        <script scriptType ="python">
            <![CDATA[import assemble_v2;assemble_v2.tab_in(hou.node('/obj'),\'$NAME\')
            ]]>
        </script>
    </tool>

</shelfDocument>
'''


def writeXML(assetName='None',context='OBJ'):
    project=Project()
    asset_body=project.get_body(assetName)
    icon=os.path.join('$JOB','byu-pipeline-tools','assets','images','icons','tool-icons','2.png')

    if not asset_body.is_asset():
        print('error me this')
        raise Exception('Failed to generate XML for: '+ assetName +' \n Object is not an Asset')



    global baseXML
    xml=Template(baseXML).substitute(NAME=assetName,LABEL=assetName.replace('_',' ').title(),ICON=icon,CONTEXT=context)

    try:
        path=os.path.join(project.get_assets_dir(),assetName)
        path=os.path.join(path,assetName+'.shelf')


        file=open(path,'w')
        file.write(xml)
        file.close()

        if not os.path.exists(project.get_tabs_dir()):
            os.makedirs(project.get_tabs_dir())

        sym=os.path.join(project.get_tabs_dir(),assetName+'.shelf')

        if os.path.exists(sym):
            os.unlink(sym)
        os.link(path,sym)

    except Exception as e:
        print e
        raise Exception('Failed to generate XML for: '+ assetName)
