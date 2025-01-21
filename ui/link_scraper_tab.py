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
    # Conditional Inputs Based on Strategy
    if scraping_strategy == "Pagination":
        pagination_urls = st.text_area(
            "Pagination URL Templates",
            placeholder="https://example.com/page={page_number}, https://example2.com/page={page_number}",
            help="Use {page_number} as a placeholder for page numbers. Separate multiple URLs with commas."
        )

        # Split the input by commas and remove extra spaces
        pagination_url_list = [url.strip() for url in pagination_urls.split(',') if url.strip()]

        st.write("List of Pagination URL Templates:", pagination_url_list)
        # max_pages = st.number_input("Maximum Pages to Scrape", min_value=1, max_value=99999, value=5)
    
    elif scraping_strategy == "Next Button":
        next_button_selector = st.text_input("Next Button Selector", placeholder="button.next-page")
        max_pages = st.number_input("Maximum Pages to Scrape", min_value=1, max_value=99999, value=5)

    elif scraping_strategy == "Scroll/Load More":
        have_load_more_button = True if st.selectbox("Have Load More Button?", ["Yes", "No"]) == "Yes" else False
        load_more_selector = st.text_input("Load More Button Selector", placeholder="button.load-more")

    elif scraping_strategy == "Custom":
        st.warning("Custom strategy logic is not implemented yet.")
        custom_strategy = True

    if scraping_strategy != "Pagination":
        base_urls = st.text_area("Base URLs", placeholder="https://example.com, https://example2.com")
        url_list = [url.strip() for url in base_urls.split(',') if url.strip()]
        st.write("List of URLs:", url_list)
    
    link_selectors = st.text_area(
        "Link Selectors (CSS)",
        placeholder="a.link-class, div.card a, h3.title a",
        help="Enter multiple CSS selectors separated by commas."
    )

    # Split the input by commas and clean up whitespace
    link_selector_list = [selector.strip() for selector in link_selectors.split(',') if selector.strip()]
    st.write("List of CSS Link Selectors:", link_selector_list)

    max_pages = st.text_input(
        "Enter Your Web Pages Limit (Separate By Commas)",
        placeholder="3,4,5,6",
        help="Enter Max Pages separated by commas."
    )
    max_pages_list = [page.strip() for page in max_pages.split(',') if page.strip()]


    pagination_url = None
    next_button_selector = None
    load_more_selector = None
    have_load_more_button = False
    custom_strategy = False
    max_pages = 5
    multiple_links = st.selectbox("Enable Multiple Links", ["False", "True"]) == "True"  # Dropdown for enabling multiple links



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
                    base_url = url_list if scraping_strategy != "Pagination" else ["WWW.Gadang.com"] * len(link_selectors),
                    link_selector=link_selector_list,
                    pagination_url=pagination_url_list if scraping_strategy == "Pagination" else None,
                    next_button_selector=next_button_selector,
                    load_more_selector=load_more_selector,
                    have_load_more_button=have_load_more_button,
                    custom_strategy=custom_strategy,
                    max_pages=max_pages_list,
                    multiple_links=multiple_links
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
