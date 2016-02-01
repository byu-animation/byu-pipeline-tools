from byuam.body import Asset, Shot
from byuam.environment import Department
from byuam.element import Element
from byuam.project import Project
import getpass
import os
import shutil

project = Project()
shot = project.create_shot("a01")
anim = shot.get_element(Department.ANIM)

print anim.get_name()
print anim.get_parent_name()
print anim.get_department()
print anim.get_status()

#cur_user = getpass.getuser()
#cur_user_dir = os.path.join(project.get_users_dir(), cur_user)
#os.mkdir(cur_user_dir)
#checkout_file = anim.checkout(cur_user)
#print checkout_file
#shutil.rmtree(cur_user_dir)

shutil.rmtree(project.get_shots_dir()) # NEVER DO THIS IN REAL LIFE
os.mkdir(project.get_shots_dir())

asset = project.create_asset("firefly")
model = asset.get_element(Department.MODEL)

print model.get_name()
print model.get_parent_name()
print model.get_department()
print model.get_status()

shutil.rmtree(project.get_assets_dir()) # NEVER DO THIS IN REAL LIFE
os.mkdir(project.get_assets_dir())
