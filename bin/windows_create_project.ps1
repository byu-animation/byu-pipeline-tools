 param (
    [string]$name = "LocalPipeline",
    [string]$nickname = "Pip"
 )

$pwd = split-path -parent $MyInvocation.MyCommand.Definition
$windows_env_location = (split-path -parent $pwd) + "\app-launch-scripts"
cd $windows_env_location
&'.\windows_env.ps1'
cd $pwd

$create_project_command = " " + $env:BYU_PROJECT_DIR + " " + $name + " --nickname " + $nickname
echo ("About to create project with specifications: " + $create_project_command)

Write-Host 'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');

python create_project $env:BYU_PROJECT_DIR $name --nickname $nickname

Write-Host 'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');