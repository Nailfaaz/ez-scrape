import os
import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class LinkScraper:
    def __init__(self, project_folder, log_callback=None):
        """
        Initialize the LinkScraper with WebDriver and configurations.
        """
        self.project_folder = project_folder
        self.driver = self._setup_webdriver()
        self.wait = WebDriverWait(self.driver, 20)
        self.csv_path = os.path.join(self.project_folder, "links.csv")
        self.log_callback = log_callback or (lambda message: None)
        self.multiple_links=False
        os.makedirs(self.project_folder, exist_ok=True)


        # Create CSV if it doesn't exist
        if not os.path.exists(self.csv_path):
            pd.DataFrame(columns=["link"]).to_csv(self.csv_path, index=False)

    def _setup_webdriver(self):
        """
        Set up Chrome WebDriver with headless options.
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")

        prefs = {
            "download.prompt_for_download": False,
            "download.default_directory": self.project_folder,
            "profile.default_content_setting_values.automatic_downloads": 1,
        }
        options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=options)

    def _log(self, message):
        """
        Log messages through the callback.
        """
        logging.info(message)
        self.log_callback(message)

    def _extract_links(self, link_selector):
        """
        Extract links using a CSS selector.
        """
        try:
            self._log(f"Extracting links using selector: {link_selector}")
            elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, link_selector))
            )
            links = {element.get_attribute("href") for element in elements if element.get_attribute("href")}
            self._log(f"Found {len(links)} unique links.")
            return links
        except TimeoutException:
            self._log(f"Timeout while extracting links with selector: {link_selector}")
            return set()
        except Exception as e:
            self._log(f"Error while extracting links: {e}")
            return set()

    def _save_links(self, links):
        """
        Save new links to the CSV file.
        """
        if not links:
            return
        try:
            existing_links = set(pd.read_csv(self.csv_path)["link"]) if os.path.exists(self.csv_path) else set()
            new_links = links - existing_links
            if new_links:
                pd.DataFrame(new_links, columns=["link"]).to_csv(
                    self.csv_path, mode="a", header=False, index=False
                )
                self._log(f"Saved {len(new_links)} new links.")
        except Exception as e:
            self._log(f"Error saving links: {e}")

    def _scroll_and_load(self, link_selector, load_more_selector=None):
        """
        Scroll through the page and optionally click a "Load More" button.
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            links = self._extract_links(link_selector)
            self._save_links(links)
            time.sleep(2)

            if load_more_selector:
                try:
                    button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, load_more_selector)))
                    button.click()
                    self._log("Clicked 'Load More' button.")
                    time.sleep(2)
                except Exception as e:
                    self._log(f"Load more button interaction failed: {e}")

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _scroll_and_load_only(self, link_selector, footer_selector, max_scrolls=50, wait_time=3, max_repeats=3):
        """
        Scroll through the page and load more content by scrolling near the footer.
        Stops when the same set of links is observed for a specified number of consecutive scrolls.
        """
        seen_links = set()
        scroll_count = 0
        repeat_count = 0

        while scroll_count < max_scrolls:
            try:
                footer = self.driver.find_element(By.CSS_SELECTOR, footer_selector)
                footer_location = footer.location['y']

                scroll_position = footer_location - 200
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                self._log(f"Scrolled to position {scroll_position}, above the footer.")
            except Exception as e:
                self._log(f"Footer not found or could not calculate position: {e}")
                break

            time.sleep(wait_time) 

            links = self._extract_links(link_selector)
            new_links = set(links) - seen_links  
            if new_links:
                seen_links.update(new_links) 
                repeat_count = 0
                self._log(f"Found {len(new_links)} new links, {len(seen_links)} total links.")
            else:
                repeat_count += 1
                self._log(f"No new links found for {repeat_count} consecutive scrolls.")
            self._save_links(new_links)

            if repeat_count >= max_repeats:
                self._log(f"Same links observed for {max_repeats} consecutive scrolls. Stopping scrolling.")
                break
            scroll_count += 1

        self._log(f"Scrolling finished after {scroll_count} scrolls. Total links collected: {len(seen_links)}.")

    def scrape(self, base_urls, link_selectors, pagination_url=None, next_button_selector=None,
           load_more_selector=None, have_load_more_button=False, custom_strategy=None, 
           max_pages=5, progress_callback=None, multiple_links=False):
        """
        Perform the scraping using the specified strategy.
        """

        # Prepare URL and selector pairs based on whether multiple links are involved
        if multiple_links:
            url_selector_pairs = []
            if pagination_url:
                url_selector_pairs.extend(zip(base_urls, link_selectors, pagination_url))
            elif next_button_selector:
                url_selector_pairs.extend(zip(base_urls, link_selectors, next_button_selector))
            else:
                # Fallback if no pagination or next button strategy is defined
                url_selector_pairs.extend(zip(base_urls, link_selectors, ["Default"] * len(base_urls)))
        else:
            url_selector_pairs = [(base_urls, link_selectors, "Default")]

        for current_url, link_selector, next_page in url_selector_pairs:
            self.driver.get(current_url)
            self._log(f"Starting scraping at {current_url}")
            current_page = 1

            while True:
                self._log(f"Processing page {current_page}")

                if custom_strategy:
                    self._log("Using custom strategy.")
                    self._apply_custom_strategy(custom_strategy)
                    break

                # Extract and save links on the current page
                links = self._extract_links(link_selector)
                self._save_links(links)

                # Handle pagination strategies
                if pagination_url:
                    try:
                        if not multiple_links : 
                            next_page=pagination_url
                        next_url = next_page.format(page_number=current_page + 1)
                        self._log(f"{next_url,next_page} anjay")
                        self.driver.get(next_url)
                    except Exception as e:
                        self._log(f"Pagination ended: {e}")
                        break

                elif next_button_selector:
                    try:
                        next_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, next_page)))
                        next_button.click()
                    except (TimeoutException, NoSuchElementException):
                        self._log("No more pages to navigate.")
                        break

                elif load_more_selector:
                    # Handle the "load more" button strategy
                    if have_load_more_button:
                        self._scroll_and_load(link_selector, load_more_selector)
                    else:
                        self._scroll_and_load_only(link_selector, load_more_selector)
                    break

                else:
                    self._log("No pagination strategy defined, ending scrape.")
                    break

                # Update page number and handle progress
                
                if progress_callback:
                    progress_value = min(current_page / max_pages, 1.0)
                    progress_callback(progress_value, f"Page {current_page} of {max_pages}")

                if max_pages and current_page >= max_pages:
                    self._log("Reached maximum page limit.")
                    break
                current_page += 1


    def close(self):
        """
        Close the WebDriver.
        """
        self.driver.quit()


def scrapelinksmain(project_folder, base_url, link_selector, pagination_url=None,
                    next_button_selector=None, load_more_selector=None, have_load_more_button=None,
                    custom_strategy=None, max_pages=5,multiple_links=False):
    """
    Main function for scraping links with real-time logging and progress tracking.
    """
    from collections import deque
    import streamlit as st

    log_stream = deque(maxlen=10)
    log_placeholder = st.empty()
    progress_placeholder = st.empty()

    def log_callback(message):
        log_stream.append(message)
        log_placeholder.text("\n".join(log_stream))

    def progress_callback(value, message):
        progress_placeholder.progress(value, text=message)

    scraper = LinkScraper(project_folder, log_callback)

    try:
        scraper.scrape(
            base_urls=base_url,
            link_selectors=link_selector,
            pagination_url=pagination_url,
            next_button_selector=next_button_selector,
            load_more_selector=load_more_selector,
            have_load_more_button=have_load_more_button,
            custom_strategy=custom_strategy,
            max_pages=max_pages,
            progress_callback=progress_callback,
            multiple_links=multiple_links
        )
    except Exception as e:
        log_callback(f"Scraping failed: {e}")
        raise
    finally:
        scraper.close()
        progress_placeholder.empty()
