"""
@author Hunter Tinney
created python versions of the python_env script so that it could work with hbatch after Houdini is opened
"""


import os

def safe_append(varname, value):

    if varname not in os.environ:
        os.environ[varname] = ""
    os.environ[varname] += value

def project_env():

    scriptLocation = os.path.dirname(os.path.realpath(__file__))
    toolsDir = os.path.dirname(scriptLocation)
    projectDir = os.path.dirname(toolsDir)
    os.environ["BYU_PROJECT_DIR"] = projectDir
    os.environ["BYU_TOOLS_DIR"] = toolsDir
    safe_append("PYTHONPATH", ":/opt/3rdParty/lib/python2.7/site-packages:/usr/lib64/python2.7/site-packages:/opt/hfs.current/houdini/python2.7libs")

def project_houdini():

    project_env()
    os.environ["CURRENT_PROG"] = "houdini"
    os.environ["HOUDINI_USE_HFS_PYTHON"] = "1"
    os.environ["JOB"] = os.environ["BYU_PROJECT_DIR"]
    houdini_tools = os.path.join(os.environ["BYU_TOOLS_DIR"], "houdini-tools")
    tractor_author = "/opt/pixar/Tractor-2.2/lib/python2.7/site-packages"
    safe_append("PYTHONPATH", ":{0}:{1}".format(houdini_tools, tractor_author))
    safe_append("HOUDINI_PATH", ":{0}:{1}:{2}".format(houdini_tools, os.environ["BYU_PROJECT_DIR"] + "/production;&", os.environ["BYU_PROJECT_DIR"] + "/production/hda;&"))
    safe_append("HOUDINI_DSO_PATH", ":{0}".format(os.environ["BYU_PROJECT_DIR"] + "/production/dso;&"))
    os.environ["HODUINI_DEFAULT_RIB_TARGET"] = "prman21.0.byu"
    os.environ["HOUDINI_MENU_PATH"] = houdini_tools + "/houdini-menus;&"
    os.environ["HOUDINI_TOOLBAR_PATH"] = os.environ["BYU_PROJECT_DIR"] + "/production/tabs;&"
    os.environ["HOUDINI_UI_ICON_PATH"] = os.environ["BYU_TOOLS_DIR"] + "/assets/images/icons/tool-icons;&"
