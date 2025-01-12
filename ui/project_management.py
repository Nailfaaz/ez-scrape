import streamlit as st
import os
from core.project_manager import ProjectManager


def display_tree(output_root):
    if not os.path.exists(output_root):
        st.write("No projects available.")
        return

    for project in sorted(os.listdir(output_root)):
        project_path = os.path.join(output_root, project)
        if os.path.isdir(project_path):
            st.write(f"{project}")  # Display project name
            subprojects = [
                subproject
                for subproject in sorted(os.listdir(project_path))
                if os.path.isdir(os.path.join(project_path, subproject))
            ]
            for subproject in subprojects:
                st.write(f"* {subproject}")  # Display subproject name


def project_management_sidebar(output_root):
    """
    Streamlit sidebar for project and subproject management with "Add New" buttons and output tree display.
    """
    st.header("Project Management")

    # Initialize session state
    if "current_project" not in st.session_state:
        st.session_state["current_project"] = None
    if "current_subproject" not in st.session_state:
        st.session_state["current_subproject"] = None
    if "add_new_project" not in st.session_state:
        st.session_state["add_new_project"] = False
    if "add_new_subproject" not in st.session_state:
        st.session_state["add_new_subproject"] = False

    # Initialize ProjectManager
    project_manager = ProjectManager(output_root)

    # Fetch projects dynamically
    projects = project_manager.get_projects()

    # Project Selection
    project_name = st.selectbox(
        "Select Project",
        ["--Select a Project--"] + projects,
        key="project_selector",
    )

    if project_name != "--Select a Project--":
        st.session_state["current_project"] = project_name
        st.session_state["current_subproject"] = None  # Reset subproject when project changes
        st.success(f"Project '{project_name}' selected.")
    else:
        st.session_state["current_project"] = None

    # "Add New Project" Button
    if st.button("Add New Project", key="add_new_project_button"):
        st.session_state["add_new_project"] = True

    # Input for New Project (shown only after clicking "Add New Project")
    if st.session_state["add_new_project"]:
        new_project_name = st.text_input("Enter New Project Name", key="new_project_input")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Save New Project", key="save_new_project"):
                if new_project_name.strip():
                    success, message = project_manager.create_project(new_project_name)
                    if success:
                        st.success(message)
                        st.session_state["add_new_project"] = False  # Reset the "Add New" state
                    else:
                        st.error(message)
                else:
                    st.warning("Project name cannot be empty.")
        with col2:
            if st.button("Cancel New Project", key="cancel_new_project"):
                st.session_state["add_new_project"] = False  # Reset the "Add New" state

    # If a project is selected, show subproject options
    if st.session_state["current_project"]:
        # Fetch subprojects dynamically
        subprojects = project_manager.get_subprojects(st.session_state["current_project"])

        # Subproject Selection
        subproject_name = st.selectbox(
            "Select Subproject",
            ["--Select a Subproject--"] + subprojects,
            key="subproject_selector",
        )

        if subproject_name != "--Select a Subproject--":
            st.session_state["current_subproject"] = subproject_name
            st.success(f"Subproject '{subproject_name}' selected.")
        else:
            st.session_state["current_subproject"] = None

        # "Add New Subproject" Button
        if st.button("Add New Subproject", key="add_new_subproject_button"):
            st.session_state["add_new_subproject"] = True

        # Input for New Subproject (shown only after clicking "Add New Subproject")
        if st.session_state["add_new_subproject"]:
            new_subproject_name = st.text_input("Enter New Subproject Name", key="new_subproject_input")
            col3, col4 = st.columns([1, 1])
            with col3:
                if st.button("Save New Subproject", key="save_new_subproject"):
                    if new_subproject_name.strip():
                        success, message = project_manager.create_subproject(
                            st.session_state["current_project"], new_subproject_name
                        )
                        if success:
                            st.success(message)
                            st.session_state["add_new_subproject"] = False  # Reset the "Add New" state
                        else:
                            st.error(message)
                    else:
                        st.warning("Subproject name cannot be empty.")
            with col4:
                if st.button("Cancel New Subproject", key="cancel_new_subproject"):
                    st.session_state["add_new_subproject"] = False  # Reset the "Add New" state

    # Display Current Selections
    st.divider()
    st.write("**Current Selections:**")
    st.write(f"Project: {st.session_state['current_project'] or 'None'}")
    st.write(f"Subproject: {st.session_state['current_subproject'] or 'None'}")

    # Display Output Tree (Formatted)
    st.divider()
    st.write("**Project Structure:**")
    display_tree(output_root)
