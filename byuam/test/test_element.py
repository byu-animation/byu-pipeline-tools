from byuam.body import Asset, Shot
from byuam.department import Department
from byuam.element import Element
from byuam.project import Project
import os
import shutil

project = Project()
shot = project.create_shot("a01")
anim = shot.create_element(Department.ANIM)

print anim.get_name()
print anim.get_department()
print anim.get_status()

shutil.rmtree(project.get_shots_dir()) # NEVER DO THIS IN REAL LIFE
os.mkdir(project.get_shots_dir())

asset = project.create_asset("firefly")
model = asset.create_element(Department.MODEL)

print model.get_name()
print model.get_department()
print model.get_status()

shutil.rmtree(project.get_assets_dir()) # NEVER DO THIS IN REAL LIFE
os.mkdir(project.get_assets_dir())
