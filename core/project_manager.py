import os

class ProjectManager:
    def __init__(self, output_root):
        self.output_root = output_root

    def get_projects(self):
        """Retrieve the list of projects."""
        return [
            project for project in os.listdir(self.output_root)
            if os.path.isdir(os.path.join(self.output_root, project))
        ]

    def create_project(self, new_project_name):
        """Create a new project directory."""
        try:
            project_path = os.path.join(self.output_root, new_project_name)
            os.makedirs(project_path, exist_ok=True)
            return True, f"Project '{new_project_name}' created successfully."
        except Exception as e:
            return False, str(e)

    def get_subprojects(self, current_project):
        """Retrieve the list of subprojects for a specific project."""
        if not current_project:
            return []
        project_path = os.path.join(self.output_root, current_project)
        return [
            subproject for subproject in os.listdir(project_path)
            if os.path.isdir(os.path.join(project_path, subproject))
        ]

    def create_subproject(self, current_project, new_subproject_name):
        """Create a new subproject directory with standard subfolders."""
        try:
            if not current_project:
                return False, "No project selected."

            subproject_path = os.path.join(self.output_root, current_project, new_subproject_name)
            os.makedirs(subproject_path, exist_ok=True)

            # Create standard subfolders
            subdirs = ["pdfs", "links", "warcs", "tokens", "compressed"]
            for subdir in subdirs:
                os.makedirs(os.path.join(subproject_path, subdir), exist_ok=True)

            return True, f"Subproject '{new_subproject_name}' created successfully."
        except Exception as e:
            return False, str(e)
