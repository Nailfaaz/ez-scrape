"""
custom_link_scraper.py

This file serves as a placeholder for users to implement their own custom link scraping functionality.
Key functionalities such as saving links to the "links" folder are provided. Users can add their own
custom scraping logic while maintaining compatibility with the default structure.

Instructions:
1. Customize the `scrape` method to add your scraping logic.
2. Use `_extract_links` and `_save_links` to handle link extraction and saving.
3. Ensure all links are saved in the CSV format under the "links" folder.
"""

import os
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class CustomLinkScraper:
    def __init__(self, project_folder, log_callback=None):
        """
        Initialize the CustomLinkScraper with project folder setup and logging.
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
        Extract links using a CSS selector. Users can customize this logic.
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

    def scrape(self, **kwargs):
        """
        Custom scraping logic goes here. Customize as needed.
        
        Parameters:
            kwargs: Dynamic arguments for flexibility (e.g., URL, CSS selectors, etc.).
        
        Example Usage:
            - Pass URL and link selector to extract and save links.
        """
        self._log("Custom scraping logic not implemented. Please customize the `scrape` method.")
