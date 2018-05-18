
#!/bin/sh

# project_nuke.sh: opens nuke  with the project environment

# source project environment
#DIR=`dirname $0`
#source ${DIR}/project_env.sh

#export CURRENT_PROG='Nuke'

# Change directories so current directory is not in the tools folder
#cd ${USER_DIR}

echo "Starting Nuke..."
export LD_PRELOAD=/usr/lib64/libstdc++.so.6:/lib64/libgcc_s.so.1
/usr/local/Nuke10.5v7/Nuke10.5 -b --nukex
