import os
import pandas as pd
import streamlit as st
from core.scrapers.warc_scraper import WarcScraper
import time
def warc_scraper_tab(output_root):
    st.header("WARC Scraper")

    # Check project/subproject
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
    warcs_folder = os.path.join(subproject_folder, "warcs", "scraped-warcs")

    # Show `links.csv`
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

    # Progress bar
    progress_bar = st.empty()
    log_placeholder = st.empty()

    def update_progress(current, total, message=""):
        progress_bar.progress(current / total, text=message)
    def elapsed_time(start_time,end_time) :
            elapsed_seconds = round(end_time, 2)
            elapsed_minutes = round(end_time / 60, 2)
            st.write(f"Elapsed time: {elapsed_seconds} seconds ({elapsed_minutes} minutes)")


    # Start scraping
    if st.button("Start WARC Scraping"):
        scraper = WarcScraper(subproject_folder, log_callback=lambda msg: log_placeholder.text(msg))
        with st.spinner("Scraping URLs..."):
            try:
                start_time=time.time()
                scraper.scrape_csv(links_csv_path, update_progress)
                end_time=time.time()-start_time
                elapsed_time(start_time,end_time)
                st.success("WARC scraping completed!")
                st.write(f"WARC files saved to: `{warcs_folder}`")
            except Exception as e:
                st.error(f"Scraping failed: {e}")
