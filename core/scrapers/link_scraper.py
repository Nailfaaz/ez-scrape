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

    def scrape(self, base_url, link_selector, pagination_url=None, next_button_selector=None,
               load_more_selector=None, custom_strategy=None, max_pages=5, progress_callback=None):
        """
        Perform the scraping using the specified strategy.
        """
        self.driver.get(base_url)
        self._log(f"Starting scraping at {base_url}")
        current_page = 1

        while True:
            self._log(f"Processing page {current_page}")

            if custom_strategy:
                self._log("Custom strategy is not implemented.")
                break

            if pagination_url:
                links = self._extract_links(link_selector)
                self._save_links(links)
                try:
                    next_url = pagination_url.format(page_number=current_page + 1)
                    self.driver.get(next_url)
                except Exception as e:
                    self._log(f"Pagination ended: {e}")
                    break
                current_page += 1

            elif next_button_selector:
                links = self._extract_links(link_selector)
                self._save_links(links)
                try:
                    next_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector)))
                    next_button.click()
                except (TimeoutException, NoSuchElementException):
                    self._log("No more pages to navigate.")
                    break
                current_page += 1

            elif load_more_selector:
                self._scroll_and_load(link_selector, load_more_selector)

            else:
                break

            if progress_callback:
                progress_value = min(current_page / max_pages, 1.0)
                progress_callback(progress_value, f"Page {current_page} of {max_pages}")
            if max_pages and current_page >= max_pages:
                break

    def close(self):
        """
        Close the WebDriver.
        """
        self.driver.quit()


def scrapelinksmain(project_folder, base_url, link_selector, pagination_url=None,
                    next_button_selector=None, load_more_selector=None,
                    custom_strategy=None, max_pages=5):
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
            base_url, link_selector, pagination_url, next_button_selector,
            load_more_selector, custom_strategy, max_pages, progress_callback
        )
    except Exception as e:
        log_callback(f"Scraping failed: {e}")
        raise
    finally:
        scraper.close()
        progress_placeholder.empty()
