import os
import streamlit as st
from core.token_estimator import TokenEstimator

def token_estimator_tab(output_root):
    """
    Streamlit tab for token estimation from PDFs and WARCs.
    """
    st.header("Token Estimator")

    # Check project and subproject
    if not (st.session_state.get("current_project") and st.session_state.get("current_subproject")):
        st.error("Please select a Project and Subproject in the sidebar before using this feature.")
        return

    # Define paths and estimator
    project_name = st.session_state["current_project"]
    subproject_name = st.session_state["current_subproject"]
    project_folder = os.path.join(output_root, project_name, subproject_name)

    estimator = TokenEstimator(project_folder)

    # PDF Token Estimation
    pdf_folder = os.path.join(project_folder, "pdfs", "scraped-pdfs")
    if os.path.exists(pdf_folder) and any(f.endswith(".pdf") for f in os.listdir(pdf_folder)):
        if st.button("Estimate Tokens for PDFs"):
            with st.spinner("Estimating tokens for PDFs..."):
                try:
                    estimator.process_pdfs(pdf_folder)
                    st.success("Token estimation for PDFs completed!")
                except Exception as e:
                    st.error(f"PDF token estimation failed: {e}")

    # WARC Token Estimation
    warc_folder = os.path.join(project_folder, "warcs", "scraped-warcs")
    if os.path.exists(warc_folder) and any(f.endswith(".warc") for f in os.listdir(warc_folder)):
        css_selector = st.text_input(
            "Optional CSS Selector for WARC Token Estimation",
            placeholder="e.g., div.article-content"
        )
        if st.button("Estimate Tokens for WARCs"):
            with st.spinner("Estimating tokens for WARCs..."):
                try:
                    use_css_selector = bool(css_selector.strip())
                    estimator.process_warcs(warc_folder, use_css_selector=use_css_selector, css_selector=css_selector)
                    st.success("Token estimation for WARCs completed!")
                except Exception as e:
                    st.error(f"WARC token estimation failed: {e}")

    # If neither PDFs nor WARCs are available
    if not os.path.exists(pdf_folder) and not os.path.exists(warc_folder):
        st.warning("No PDFs or WARCs found in the selected project/subproject.")
