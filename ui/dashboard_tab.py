import streamlit as st
import pandas as pd
from core.dashboard import get_project_level_stats, get_subproject_level_stats

def dashboard_tab(output_root):
    """
    Streamlit tab for the project dashboard.
    """
    st.header("Dashboard")

    # Project-Level Statistics
    st.subheader("Project-Level Summary")
    project_data = get_project_level_stats(output_root)
    if project_data:
        project_df = pd.DataFrame(
            project_data,
            columns=["Project", "Files Count", "Token Count", "Project Size (Bytes)", "Project Compressed Size (Bytes)"]
        )
        st.dataframe(project_df, use_container_width=True)
    else:
        st.warning("No project-level data available.")

    # Subproject-Level Statistics
    st.subheader("Subproject-Level Details")
    subproject_data = get_subproject_level_stats(output_root)
    if subproject_data:
        subproject_df = pd.DataFrame(
            subproject_data,
            columns=["Project", "Subproject", "Files Count", "Token Count", "Folder Size (Bytes)", "Folder Compressed Size (Bytes)"]
        )
        st.dataframe(subproject_df, use_container_width=True)
    else:
        st.warning("No subproject-level data available.")
