# byu-pipeline-tools

Asset management tools for BYU Animation

To setup a test environment, first copy project_env.sh and replace the following two lines with the path to your project and fork of the repository:

```
export BYU_PROJECT_DIR=/path/to/project
export BYU_TOOLS_DIR=/path/to/byu-pipeline-tools
```

Then run the script:

```
source project_env.sh
```

And create an empty project:

```
create_project $BYU_PROJECT_DIR
```