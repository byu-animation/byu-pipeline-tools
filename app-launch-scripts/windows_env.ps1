$scriptlocation = split-path -parent $MyInvocation.MyCommand.Definition
cd $scriptlocation

$projectDir = (get-item $scriptlocation).parent.parent.FullName
$env:BYU_PROJECT_DIR = $projectDir
$env:BYU_TOOLS_DIR = (join-path $projectDir "byu-pipeline-tools")
$env:PYTHONPATH += $env:BYU_TOOLS_DIR + ";&"