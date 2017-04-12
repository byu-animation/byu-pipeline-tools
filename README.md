#Asset Management Tools for BYU Animation

## Installation
---
To setup a project:

1. Clone the project into the desired directory and navigate into the byu-pipeline-tools directory.
1. Set up all the necessary environment variables with the following script:
	```bash
	source app-launch-scripts/project_env.sh
	```
1. Run this script to create an new set of project directory in which the project assets and user info will be stored:
	```bash
	create_project $BYU_PROJECT_DIR
	```
1. For all of the byu-[TOOL].desktop files change the line bellow to have the path to the launch script.
	```text
	Exec=/path/to/project/byu-pipeline-tools/app-launch-scripts/project_[TOOL].sh
	```
It would be nice to not have to change that but I don't really know how. Everybody should be able to make a copy to their desktop and if they don't have the absolute path then how will it find the script? I suppose in the future you could make everybody make a shortcut to the .desktop files but at this point I think that it would be more difficult them to educate them on that... And there would be a bunch of people that will just copy them out anyways. I think it would be better to just keep it this way.
1. Update all of the images to be customized for your project.
	* Update the icons for the .desktop files
		* Icon images of for the .desktop files can be found in byu-pipeline-tools/assets/images/icons/
		* There is a gimp file that you can use for easy creation of custom icons in byu-pipeline-tools/assets/images/icons/maker/
			* Just make the changes you want and export the icon once for each tool with the desired tool's icon layer visible.
	* Update the banner image
		* The banner image is shown on several of the tools. Overwrite byu-pipeline-tools/byugui/assets/images/film-banner.jpg with your own image.
1. Set up the email
1. Pray that everything holds together
1. Let the artist have at it. They will let you know if anything is broken.

## Explanation of All the Files
---
### app-launch-scripts
Here lies all of of the scripts that load in the custom tools and launches the software. Most of them will be discussed in more detail in the basic overview of the tools.
#### project_env.sh
This script sets all of the environment variables that most of the programs need and all of the other scripts call this script. If many programs need something add it here. If just one needs it add it to the appropriate script.
### assets
Any file that is not code that is needed by the general body of the code can be found here. We have icons, images, test geometry and more!
### bin
I don't really know what these do. Except that the create_project script is housed here.
### byuam
This folder holds all the code for the Project Browser which will be discussed later.
### byugui
This folder holds all the common gui elements that our custom tools use.
byugui/assets has some images that data that some of the elements use.
### FileZilla3
I don't know what is in here or why we have it here.
### tools Folders
These will be discussed in the next section.

## Basic Overview of the Tools
---
### Maya
All of the Maya tools are located in maya-tools/. When project_maya.sh launches Maya, Maya will look in the maya-tools/shelf/shelf.json for how to make the Maya shelf for the BYU tools.

To add a tool to Maya:

1. Add an icon in the shelf/icons directory. It will need to be a 33x33 .xpm icon file.
1. Add a python script into the shelf/scripts directory.
	* Follow the examples of other scripts. The inspire_quote.py demonstrates a fairly simple script that can be used as a starting point.
	* The most important thing is that you have a go() function. This is what the shelf tool in Maya will call when the user pressed the button.
1. Follow the pattern in shelf.json to add another button to the shelf. Make sure to add the path to your icon and script into the new button.
Most unfortunately Maya needs to be restarted every time you change your script. So have fun with that!
### Houdini
For Houdini the shelf is make by houdini-tools/toolbar/byu_tools.shelf.
Each tool has it's own shelf folder in that directory.

To add a tool to Houdini:

1. Write a python script for your tool and save it in houdini-tools/
1. Make your_tool.shelf file following the examples of the other .shelf files. This file should reference the script you made.
1. Add ``<memberTool name="your_tool"/>`` to byu_tools.shelf.
### Mari
Mari doesn't have any tools made for it yet. You will have the unique opportunity of learning how to make tools for it from scratch. Since they Mary and Nuke are both made by The Foundry I would imagine the process would be fairly similar to each other, so you could use the Nuke tools as a guide.
### Nuke
Nuke will use nuke-tools/menu.py to generate the menu for the BYU-tools.

To add a tool to Nuke:

1. Make a 33x33 .xpm icon and add it to nuke-tools/icons/
1. Make a python script and add it to nuke-tools/scripts/
1. In menu.py add ``m.addCommand("Your Tool", 'yourScript.go()', icon="yourIcon.xpm")``
### Project Browser
The Project Browser give a way to easily create and manage all of the assets. Here you can make assignments and set due dates.

## Notes
---
* For the gui elements use PySide2 and a little PyQt
* These tools are designed for Linux. They are not guaranteed to work on any other operation system.
