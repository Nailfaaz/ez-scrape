import os
import streamlit as st
from core.compress import FileCompressor

def compress_tab(output_root):
    """
    Streamlit tab for compressing PDFs and WARCs.
    """
    st.header("File Compression")

    # Check project and subproject
    if not (st.session_state.get("current_project") and st.session_state.get("current_subproject")):
        st.error("Please select a Project and Subproject in the sidebar before using this feature.")
        return

    # Define paths and compressor
    project_name = st.session_state["current_project"]
    subproject_name = st.session_state["current_subproject"]
    project_folder = os.path.join(output_root, project_name, subproject_name)

    compressor = FileCompressor(project_folder, project_name, subproject_name)

    # Check availability of files
    pdf_dir = os.path.join(project_folder, "pdfs", "scraped-pdfs")
    warc_dir = os.path.join(project_folder, "warcs", "scraped-warcs")

    pdf_available = any(f.endswith(".pdf") for f in os.listdir(pdf_dir)) if os.path.exists(pdf_dir) else False
    warc_available = any(f.endswith(".warc") for f in os.listdir(warc_dir)) if os.path.exists(warc_dir) else False

    if not pdf_available and not warc_available:
        st.warning("No PDFs or WARCs available for compression.")
        return

    # Compress PDFs
    if pdf_available:
        if st.button("Compress PDFs"):
            with st.spinner("Compressing PDFs..."):
                pdf_zip_path = compressor.compress_pdfs()
                if pdf_zip_path:
                    st.success(f"PDFs compressed successfully! File saved at: `{pdf_zip_path}`")
                else:
                    st.error("Failed to compress PDFs.")

    # Compress WARCs
    if warc_available:
        if st.button("Compress WARCs"):
            with st.spinner("Compressing WARCs..."):
                warc_gz_path = compressor.compress_warcs()
                if warc_gz_path:
                    st.success(f"WARCs compressed successfully! File saved at: `{warc_gz_path}`")
                else:
                    st.error("Failed to compress WARCs.")
