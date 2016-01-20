from byuam import project

current_proj = project.Project()
print current_proj.get_project_dir()
print current_proj.get_assets_dir()
print current_proj.get_shots_dir()
print current_proj.get_users_dir()

