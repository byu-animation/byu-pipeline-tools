<#
This should be abstracted out into the windows_env.pm1 file
#>

$scriptlocation = split-path -parent $MyInvocation.MyCommand.Definition
cd $scriptlocation
$projectDir = (get-item $scriptlocation).parent.parent.FullName
$env:BYU_PROJECT_DIR = $projectDir
$env:BYU_TOOLS_DIR = (join-path $projectDir "byu-pipeline-tools")

<#
This is the program specific
#>

$env:CURRENT_PROG = "Houdini"
$env:HOUDINI_USE_HFS_PYTHON = 1
$HOUDINI_TOOLS = join-path $env:BYU_TOOLS_DIR "\houdini-tools"
$env:PYTHONPATH = $PYTHONPATH + ";" + $HOUDINI_TOOLS
$env:HOUDINI_PATH = $HOUDINI_PATH + ";" + $HOUDINI_TOOLS + ";" + (join-path $env:BYU_PROJECT_DIR "\production") + (join-path $env:BYU_PROJECT_DIR "\production\hda")
$env:HOUDINI_DSO_PATH = $HOUDINI_DSO_PATH + ";" + (join-path $env:BYU_PROJECT_DIR "\production\dso")
$env:HOUDINI_DEFAULT_RIB_TARGET="prman21.0.byu"

$env:HOUDINI_MENU_PATH = join-path $HOUDINI_TOOLS "\houdini-menus"
$env:HOUDINI_TOOLBAR_PATH = join-path $env:BYU_PROJECT_DIR "\production\tabs"
$env:HOUDINI_UI_ICON_PATH = join-path $env:BYU_TOOLS_DIR "\assets\images\icons\tool-icons"

echo $HOUDINI_MENU_PATH
echo "Starting Houdini..."


if ($env:HFS) {
    $HFS = $env:HFS
} else {
    $HFS = "C:\Program Files\Side Effects Software\Houdini 17.0.459"
}


cd $HFS
&'.\bin\hcmd.exe'