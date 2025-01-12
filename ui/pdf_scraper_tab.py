import os
import pandas as pd
import streamlit as st
from core.scrapers.pdf_scraper import pdf_scraper_main

def pdf_scraper_tab(output_root):
    st.header("PDF Scraper")

    # Check project and subproject
    if not (st.session_state.get("current_project") and st.session_state.get("current_subproject")):
        st.error("Please select a Project and Subproject in the sidebar before using this feature.")
        return

    # Define paths
    subproject_folder = os.path.join(
        output_root,
        st.session_state["current_project"],
        st.session_state["current_subproject"]
    )
    links_csv_path = os.path.join(subproject_folder, "links", "links.csv")
    pdf_output_folder = os.path.join(subproject_folder, "pdfs", "scraped-pdfs")

    # Display `links.csv` if it exists
    if os.path.exists(links_csv_path):
        st.write("### Links to Scrape")
        try:
            links_df = pd.read_csv(links_csv_path)
            st.dataframe(links_df)
        except Exception as e:
            st.error(f"Could not read `links.csv`: {e}")
    else:
        st.warning("`links.csv` not found in the current subproject.")
        return

    # Progress bar and logs
    progress_bar = st.empty()
    log_placeholder = st.empty()

    def update_progress(current, total, message=""):
        progress_bar.progress(current / total, text=message)

    def log_callback(message):
        log_placeholder.text(message)

    # Start scraping button
    if st.button("Start PDF Scraping"):
        with st.spinner("Scraping PDFs..."):
            try:
                pdf_scraper_main(links_csv_path, subproject_folder, update_progress, log_callback)
                st.success("PDF scraping completed!")
                st.write(f"PDFs saved to: `{pdf_output_folder}`")
            except Exception as e:
                st.error(f"Scraping failed: {e}")
