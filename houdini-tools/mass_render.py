import sys
import os
import subprocess
import time

#import initialize_env
#initialize_env.project_houdini()

sys.path.insert(0, '/usr/lib64/python2.7/site-packages')

print "Mass render called with {}".format(sys.argv)
print os.environ

import hou
import json
import psutil

# Import Muther data
if len(sys.argv) <= 0:
    print "No shot file specified\n"
    exit()

subtask_file = sys.argv[1]
subtask_info = {}
with open(subtask_file, "r") as f:
    subtask_info = json.load(f)
    f.close()

malformed_shot_file = False
for key in ["job_file", "render_settings_file", "shot", "profile", "priority"]:
    if key not in subtask_info:
        print "Malformed shot file. Needs: {}\n".format(key)
        malformed_shot_file = True

if malformed_shot_file:
    exit()

job_info = {}
with open(subtask_info["job_file"], "r") as f:
    job_info = json.load(f)
    f.close()

malformed_job_file = False
for key in ["job_title", "job_comment", "job_directory"]:
    if key not in job_info:
        print "Malformed job file. Needs: {}\n".format(key)
        malformed_job_file = True

if malformed_job_file:
    exit()

#Pick the newest of the hip files if there's a hip and hipnc
shot_hip_path_hipnc = os.path.join(os.environ["JOB"], "production", "shots", subtask_info["shot"], "lighting", "main", subtask_info["shot"] + "_lighting_main.hipnc")
shot_hip_path_hip = os.path.join(os.environ["JOB"], "production", "shots", subtask_info["shot"], "lighting", "main", subtask_info["shot"] + "_lighting_main.hip")
shot_hip_path = ""

if os.path.exists(shot_hip_path_hipnc):
    if not os.path.exists(shot_hip_path_hip):
        shot_hip_path = shot_hip_path_hipnc
    else:
        if os.path.getmtime(shot_hip_path_hipnc) > os.path.getmtime(shot_hip_path_hip):
            shot_hip_path = shot_hip_path_hipnc
        else:
            shot_hip_path = shot_hip_path_hip
elif os.path.exists(shot_hip_path_hip):
    shot_hip_path = shot_hip_path_hip
else:
    print "No hip file found for this shot. Please make an initial publish."
    exit()

hou.hipFile.load(shot_hip_path, True, True)

# Set all parms on render nodes

ris_drivers = []
ifd_drivers = []
tractor_submit = None

if "driver_path" in subtask_info:
    specific_driver = hou.node(subtask_info["driver_path"])
    if specific_driver:
        if node.type().name() == "ris":
            ris_drivers.append(specific_driver)
        elif node.type().name() == "ifd":
            ifd_drivers.append(specific_driver)

else:
    render_collect = None
    for child in hou.node("/out/").allSubChildren():
        if child.type().name() == "byu_render_collect_main":
            render_collect = child
            break

    if not render_collect:
        print "No BYU Render Collect node found in {}".format(subtask_info["shot"])
        exit()

    for ancestor in render_collect.inputAncestors():
        print ancestor.type().name()
        if ancestor.type().name() == "ris":
            ris_drivers.append(ancestor)
        elif ancestor.type().name() == "ifd":
            ifd_nodes.append(ancestor)
        elif ancestor.type().name() == "tractorsubmit_main":
            tractor_submit = ancestor

    if tractor_submit is None:
        print "No tractor submit node found in {}\n".format(subtask_info["shot"])
        exit()


render_settings = {}
if not os.path.isfile(subtask_info["render_settings_file"]):
    print "No render settings file found."
else:
    with open(subtask_info["render_settings_file"], "r") as f:
        render_settings = json.load(f)
        f.close()

def findRenderParm(node, renderer, setting):
    parmTemplate = None
    try:
        parmTemplate = hou.properties.parmTemplate(renderer, setting)
    except Exception as e:
        pass
    if not parmTemplate:
        print "No renderparm found with name {}".format(setting)
        return None
    return parmTemplate

def copyParm(node, parm_name, parmTemplate, value):
    try:
        if not node.parm(parm_name):
            node.addSpareParmTuple(parmTemplate, create_missing_folders=True)
        node.parm(parm_name).set(value)
    except Exception as e:
        print e

for ris in ris_drivers:
    print "Ris node: {0}".format(ris)
    for setting in render_settings:
        print "Trying to set {0} on {1} with {2}".format(setting, ris, render_settings[setting])
        parmTemplate = findRenderParm(ris, 'prman21.0', setting)
        if parmTemplate:
            copyParm(ris, setting, parmTemplate, render_settings[setting])

    ris.parm("ri_display").set("{0}/{1}/render/$OS.$F4.exr".format(job_info["job_directory"], subtask_info["shot"]))
    ris.parm("ri_device").set("openexr")

    if job_info["job_type"] == "fml":
        ris.parm("f3").setExpression("floor((ch(f2) - ch(f1)) / 3)", language=hou.exprLanguage.Hscript)

for ifd in ifd_drivers:
    for setting in render_settings:
        parmTemplate = findRenderParm(ifd, 'mantra')
        if parmTemplate:
            copyParm(ris, setting, parmTemplate, render_settings[setting])

    ifd.parm("vm_picture").set("{0}/{1}/render/$OS.$F4.exr".format(job_info["job_directory"], subtask_info["shot"]))

    if job_info["job_type"] == "fml":
        ifd.parm("f3").setExpression("floor((ch(f2) - ch(f1)) / 3)", language=hou.exprLanguage.Hscript)

# Caching with Muther
for child in hou.node("/obj/").allSubChildren():
    if child.type().name() == "byu_set":
        child.parm("read_from_disk").set(1)
        child.parm("save_to_disk").pressButton()
        child.parm("reload_from_disk").pressButton()

# Set tractor submit settings
tractor_submit.parm("job_title").set(job_info["job_title"] + "_" + subtask_info["shot"])
tractor_submit.parm("job_comment").set(job_info["job_comment"])
#tractor_submit.parm("project_directory").set(os.path.join(job_info["job_directory"], subtask_info["shot"]))
tractor_submit.parm("job_priority").set(str(subtask_info["priority"]))
tractor_submit.parm("submission_list").set("2")
tractor_submit.parm("serviceKey").set(subtask_info["profile"])
memory = hou.hscript("memory -b")
memory_bytes = []
for bytes in memory[0].split():
    try:
        memory_bytes.append(float(bytes))
    except ValueError:
        pass
num_cores = int(float(psutil.virtual_memory()[1]) / memory_bytes[0])
num_cores = subtask_info["cores"] if num_cores > subtask_info["cores"] else num_cores
tractor_submit.parm("assigned_cores").set(num_cores)

# Run a user specified script

if "scene_load_script" in render_settings and "scene_load_script" not in subtask_info:
    execfile(render_settings["scene_load_script"])
elif "scene_load_script" in subtask_info:
    execfile(subtask_info["scene_load_script"])

# Save the new file
hipfile_path = os.path.join(job_info["job_directory"], subtask_info["shot"], "hipFile.hip")
print "Saving HipFile: {0}".format(hipfile_path)
os.remove(hipfile_path)
hou.hipFile.save(file_name=hipfile_path)

print "Spooling task with:\n\thipFile memory usage:{0}\n\tavailable memory:{1}\n\tcores:{2}".format(memory_bytes[0], float(psutil.virtual_memory()[1]), num_cores)

tractor_submit.parm("submit").pressButton()
