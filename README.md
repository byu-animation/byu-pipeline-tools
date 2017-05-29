# Asset Management Tools for BYU Animation

## Installation
To setup a production project:

1. Clone the project into the desired directory and navigate into the byu-pipeline-tools directory.
1. Set up all the necessary environment variables with the following script:
	```bash
	source app-launch-scripts/project_env.sh name="YourProjectName"
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
	* Update the icon for the the Houdini Digital Assets
		* in byu-pipeline-tools/assets/images/icons/
		* It should be square and simple enough that when it is really small the resampling doesn't make it ugly.
1. Make sure the permissions are right.
1. Set up the email
1. Make sure all the software versions numbers are up to date
there is a /opt/hfs.current
1. Pray that everything holds together
1. Let the artist have at it. They will let you know if anything is broken.

Setting up a test environment is similar but a little less complicated



## Notes
* For more information be sure to checkout the wiki
* Also checkout https://byu-animation.github.io/ for a tutorial of the front-end
* For the gui elements use PySide2 and a little PyQt
* These tools are designed for Linux. They are not guaranteed to work on any other operation system. In fact they are not really guaranteed to work out side of the BYU animation lab.
