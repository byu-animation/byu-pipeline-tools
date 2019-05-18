source ${1}/.byu-pipeline-tools-beta/app-launch-scripts/project_houdini_env.sh
/opt/hfs.current/bin/hbatch -c "python ${1}/.byu-pipeline-tools-beta/houdini-tools/mass_render.py ${2}"
