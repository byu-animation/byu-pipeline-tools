$scriptlocation = split-path -parent $MyInvocation.MyCommand.Definition
cd $scriptlocation

&'.\windows_env.ps1'

if ($env:HFS) {
    $HFS = $env:HFS
} else {
    $HFS = "C:\Program Files\Side Effects Software\Houdini 17.0.400"
}

$env:Path += ";" + $HFS + '\bin'

echo $env:Path

cd $HFS
#&'.\bin\hconfig'
#echo "BEFORE"
#gci env:

$env:CURRENT_PROG = "Houdini"
$env:HOUDINI_OS = "Windows"

$env:HOUDINI_USE_HFS_PYTHON = 1
$env:JOB = $env:BYU_PROJECT_DIR
$HOUDINI_TOOLS = $env:BYU_TOOLS_DIR + "\houdini-tools"
$env:PYTHONPATH += $HFS + "\houdini\python2.7libs;" + $HOUDINI_TOOLS + ";&"
$env:HOUDINI_PATH = $HFS + ";" + $HOUDINI_TOOLS + ";" + $env:BYU_PROJECT_DIR + "\production;" + $env:BYU_PROJECT_DIR + "\production\hda;&"
$env:HOUDINI_DSO_PATH = $env:BYU_PROJECT_DIR + "\production\dso;&"
$env:HOUDINI_DEFAULT_RIB_TARGET="prman21.0.byu"
$env:HOUDINI_MENU_PATH = $env:BYU_HOUDINI_TOOLS + "\houdini-menus;&"
$env:HOUDINI_TOOLBAR_PATH = $env:BYU_PROJECT_DIR + "\production\tabs;&"
$env:HOUDINI_UI_ICON_PATH = $env:BYU_TOOLS_DIR + "\assets\images\icons\tool-icons;&"

#echo "AFTER"
#gci env:

&'.\bin\houdini.exe'
#&'.\bin\hcmd.exe'