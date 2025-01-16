import os
import pandas as pd
import streamlit as st
from core.scrapers.link_scraper import scrapelinksmain


def link_scraper_tab(output_root):
    # Check if a project and subproject are selected
    if not (st.session_state.get("current_project") and st.session_state.get("current_subproject")):
        st.error("Please select a Project and Subproject in the sidebar before using this feature.")
        return  # Prevent access to the rest of the tab

    # Scraping Strategy Selection
    scraping_strategy = st.selectbox(
        "Select Scraping Strategy",
        ["Pagination", "Next Button", "Scroll/Load More", "Custom"]
    )

    # Inputs for Scraping
    base_url = st.text_input("Base URL", placeholder="https://example.com")
    link_selector = st.text_input("Link Selector (CSS)", placeholder="a.link-class")

    pagination_url = None
    next_button_selector = None
    load_more_selector = None
    have_load_more_button = False
    custom_strategy = False
    max_pages = 5

    # Conditional Inputs Based on Strategy
    if scraping_strategy == "Pagination":
        pagination_url = st.text_input(
            "Pagination URL Template",
            placeholder="https://example.com/page={page_number}",
            help="Use {page_number} as a placeholder for page numbers."
        )
        max_pages = st.number_input("Maximum Pages to Scrape", min_value=1, max_value=99999, value=5)

    elif scraping_strategy == "Next Button":
        next_button_selector = st.text_input("Next Button Selector", placeholder="button.next-page")
        max_pages = st.number_input("Maximum Pages to Scrape", min_value=1, max_value=99999, value=5)

    elif scraping_strategy == "Scroll/Load More":
        have_load_more_button = True if st.selectbox("Have Load More Button?", ["Yes", "No"]) == "Yes" else False
        load_more_selector = st.text_input("Load More Button Selector", placeholder="button.load-more")

    elif scraping_strategy == "Custom":
        st.warning("Custom strategy logic is not implemented yet.")
        custom_strategy = True

    # Start Scraping
    if st.button("Start Link Scraping"):
        links_folder = os.path.join(
            output_root,
            st.session_state["current_project"],
            st.session_state["current_subproject"],
            "links"
        )

        with st.spinner("Scraping Links..."):
            try:
                scrapelinksmain(
                    project_folder=links_folder,
                    base_url=base_url,
                    link_selector=link_selector,
                    pagination_url=pagination_url,
                    next_button_selector=next_button_selector,
                    load_more_selector=load_more_selector,
                    have_load_more_button=have_load_more_button,
                    custom_strategy=custom_strategy,
                    max_pages=max_pages,
                )
                st.success("Link Scraping Completed!")

                # Display Scraped Links
                links_csv = os.path.join(links_folder, "links.csv")
                if os.path.exists(links_csv):
                    links_df = pd.read_csv(links_csv)
                    st.dataframe(links_df)
                else:
                    st.warning("No links found during scraping.")
            except Exception as e:
                st.error(f"Scraping failed: {e}")
