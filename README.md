# Asset Management Tools for BYU Animation

## Installation
To setup a production project:

1. Clone the project into the desired directory and navigate into the byu-pipeline-tools directory.
1. Set up all the necessary environment variables with the following script:
	```bash
	source app-launch-scripts/project_env.sh
	```
1. Run this script to create an new set of project directory in which the project assets and user info will be stored:
	```bash
	create_project $BYU_PROJECT_DIR YourProjectName --email projectSupport@email.com --password projectSupportEmailPassword --nickname name
	```
	The nick name is the a short version of the film name that you can meld with a software name. For example, for the project Grendel the nickname would be Grend and for Taijitu it would be Taij so that you get Maya to become Grendaya and Taijaya and Houdini is Grendini and Taijini etc. All of the options are optional.
1. Update all of the images to be customized for your project. (For a development or test project you may skip this step)
	* Update the icons for the .desktop files
		* Icon images of for the .desktop files can be found in byu-pipeline-tools/assets/images/icons/
		* There is a gimp file that you can use for easy creation of custom icons in byu-pipeline-tools/assets/images/icons/maker/
			* Just make the changes you want and export the icon once for each tool with the desired tool's icon layer visible.
	* Update the banner image
		* The banner image is shown on several of the tools. Overwrite byu-pipeline-tools/byugui/assets/images/film-banner.jpg with your own image.
	* Update the icon for the the Houdini Digital Assets
		* in byu-pipeline-tools/assets/images/icons/
		* It should be square and simple enough that when it is really small the resampling doesn't make it ugly.
1. Make sure all the software versions numbers are up to date in the various app launch scripts
	* One of the tricks the pipeline uses is having a short cut to the current Houdini Installation: /opt/hfs.current. Make sure this shortcut is on the current image.
1. Pray that everything holds together
1. Let the artist have at it. They will let you know if anything is broken.

## Notes
* For more information be sure to checkout [the wiki](https://github.com/byu-animation/byu-pipeline-tools/wiki)
* Also checkout https://byu-animation.github.io/ for a tutorial of the front-end
* For the gui elements use PySide2 and a little PyQt
* These tools are designed for Linux. They are not guaranteed to work on any other operation system. In fact they are not really guaranteed to work out side of the BYU animation lab.
