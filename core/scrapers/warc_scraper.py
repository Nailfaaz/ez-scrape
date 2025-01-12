import os
import csv
import time
import requests
import socket
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
import logging

class WarcScraper:
    def __init__(self, project_folder, log_callback=None):
        """
        Initialize the WARC scraper with project folder setup and logging.
        """
        self.project_folder = project_folder
        self.log_callback = log_callback or (lambda msg: None)

        # Directories for output
        self.logs_folder = os.path.join(self.project_folder, "warcs", "logs")
        self.warcs_folder = os.path.join(self.project_folder, "warcs", "scraped-warcs")

        os.makedirs(self.logs_folder, exist_ok=True)
        os.makedirs(self.warcs_folder, exist_ok=True)

        # Configure explicit logger
        self.logger = logging.getLogger("WarcScraper")
        self.logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if not self.logger.handlers:
            log_file = os.path.join(self.logs_folder, "warc_scraping.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            self.logger.addHandler(file_handler)

    def _log(self, message):
        """
        Log messages to file and optional callback.
        """
        self.logger.info(message)
        self.log_callback(message)

    def _setup_webdriver(self):
        """
        Set up Selenium WebDriver for scraping.
        """
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        return webdriver.Chrome(options=options)

    def save_website_to_warc(self, url, driver):
        """
        Save a website's content to a WARC file.
        """
        try:
            self._log(f"Scraping URL: {url}")
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            html = driver.page_source
            response = requests.get(url, verify=False)
            ip_address = socket.gethostbyname(url.split("/")[2])

            sanitized_url = url.split("go.id/")[-1].replace(".html", "").replace("/", "_").replace(":", "_")
            warc_file_path = os.path.join(self.warcs_folder, f"{sanitized_url}.warc")

            with open(warc_file_path, "wb") as f:
                writer = WARCWriter(filebuf=f, gzip=False)

                # Request record
                request_headers = [
                    ("Host", url.split("/")[2]),
                    ("User-Agent", driver.execute_script("return navigator.userAgent;")),
                    ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"),
                ]
                request_status_line = "GET / HTTP/1.1"
                http_request_headers = StatusAndHeaders(request_status_line, request_headers, is_http_request=True)
                request_payload = BytesIO()
                request_record = writer.create_warc_record(url, "request", payload=request_payload, http_headers=http_request_headers)
                request_record.rec_headers.add_header("WARC-IP-Address", ip_address)
                writer.write_record(request_record)

                # Response record
                response_status_line = f"HTTP/1.1 {response.status_code} OK"
                response_headers = [
                    ("Content-Type", response.headers.get("Content-Type")),
                    ("Server", response.headers.get("Server", "Unknown")),
                ]
                http_response_headers = StatusAndHeaders(response_status_line, response_headers)
                response_payload = BytesIO(html.encode("utf-8"))
                response_record = writer.create_warc_record(url, "response", payload=response_payload, http_headers=http_response_headers)
                response_record.rec_headers.add_header("WARC-Concurrent-To", request_record.rec_headers.get_header("WARC-Record-ID"))
                response_record.rec_headers.add_header("WARC-IP-Address", ip_address)
                writer.write_record(response_record)

            self._log(f"Saved WARC record for {url}")

        except Exception as e:
            self._log(f"Error scraping {url}: {e}")

    def scrape_from_list(self, link_list, update_progress=None):
        """
        Scrape URLs from a list and save them as WARC files.
        """
        driver = self._setup_webdriver()
        total_links = len(link_list)

        for idx, url in enumerate(link_list, start=1):
            self.save_website_to_warc(url, driver)
            if update_progress:
                update_progress(idx, total_links, f"Processed {idx}/{total_links}: {url}")

        driver.quit()

    def scrape_csv(self, csv_path, update_progress=None):
        """
        Scrape URLs from a CSV file and save them as WARC files.
        """
        try:
            with open(csv_path, "r") as f:
                reader = csv.reader(f)
                next(reader)  # Skip the header
                link_list = [row[0] for row in reader]

            self._log(f"Starting scraping for CSV: {csv_path}")
            self.scrape_from_list(link_list, update_progress)
            self._log(f"Completed scraping for CSV: {csv_path}")

        except Exception as e:
            self._log(f"Error processing CSV {csv_path}: {e}")
