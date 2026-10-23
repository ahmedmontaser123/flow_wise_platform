from .Base_controller import BaseController 
import os

class ProjectController(BaseController):
    '''
      this class aim to create a project path for each project_id 
      i have function of get_project_path that will create a project path if it does not exist and return the path
    '''

    def __init__(self):
        super().__init__()

    def get_project_path_and_create(self, project_id:str):
        project_path = os.path.join(
            self.files_dir,  # stay in assetes/files/ create project path
            project_id
        )

        if not os.path.exists(project_path):
            os.makedirs(project_path)
            return project_path


        return project_path



    def get_project_path(self, project_id:str):
        project_path = os.path.join(
            self.files_dir,
            project_id
        )

        if not os.path.exists(project_path):
            return None


        return project_path

    