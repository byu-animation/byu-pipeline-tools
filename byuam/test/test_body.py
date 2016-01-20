from byuam.body import Asset, Shot
from byuam.project import Project
import os
import shutil

project = Project()

project.create_shot("a01")
project.create_shot("a02")
shots = project.list_shots()
for shot in shots:
    print shot
a01 = project.get_shot("a01")
a02 = project.get_shot("a02")
print a01.get_name()
print a02.get_name()

shutil.rmtree(project.get_shots_dir()) # NEVER DO THIS IN REAL LIFE
os.mkdir(project.get_shots_dir())

project.create_asset("firefly")
project.create_asset("temple")
assets = project.list_assets()
for asset in assets:
    print asset
firefly = project.get_asset("firefly")
temple = project.get_asset("temple")
print firefly.get_name()
print temple.get_name()

shutil.rmtree(project.get_assets_dir()) # NEVER DO THIS IN REAL LIFE
os.mkdir(project.get_assets_dir())
