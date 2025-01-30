import os
import csv
import socket
from io import BytesIO
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
import logging
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
from io import BytesIO
import aiohttp
import socket
import os
import asyncio
import uuid
from datetime import datetime
import csv
import time

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
            # self.scrape_from_list(link_list, update_progress)
            asyncio.run(self.crawl_and_save_to_warc(link_list,self.warcs_folder,update_progress))
            self._log(f"Completed scraping for CSV: {csv_path}")

        except Exception as e:
            self._log(f"Error processing CSV {csv_path}: {e}")


    async def crawl_and_save_to_warc(self,links, warc_folder,update_progress=None):
        """
        Crawl a list of links using crawl4ai and save the content as WARC files.
        """
        # Ensure the folder exists
        os.makedirs(warc_folder, exist_ok=True)
        total_links=len(links)
        async with aiohttp.ClientSession() as session:
            for idx,url in enumerate(links,start=1):
                try:
                    # Asynchronous GET request
                    async with session.get(url, ssl=False) as response:
                        response_text = await response.text()
                        ip_address = socket.gethostbyname(url.split("/")[2])

                        # Sanitize the URL for file naming
                        sanitized_url = url.split("/")[-1].replace(".html", "").replace("/", "_").replace(":", "_")
                        warc_file_path = os.path.join(warc_folder, f"{sanitized_url}.warc")

                        with open(warc_file_path, "wb") as f:
                            writer = WARCWriter(filebuf=f, gzip=False)

                            # Request record
                            request_headers = [
                                ("Host", url.split("/")[2]),
                                ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/131.0.0.0 Safari/537.36"),
                                ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"),
                            ]
                            request_status_line = "GET / HTTP/1.1"
                            http_request_headers = StatusAndHeaders(request_status_line, request_headers, is_http_request=True)
                            request_payload = BytesIO()
                            request_record = writer.create_warc_record(url, "request", payload=request_payload, http_headers=http_request_headers)
                            request_record.rec_headers.add_header("WARC-IP-Address", ip_address)
                            writer.write_record(request_record)

                            # Response record
                            response_status_line = f"HTTP/1.1 {response.status} OK"
                            response_headers = [
                                ("Content-Type", response.headers.get("Content-Type")),
                                ("Server", response.headers.get("Server", "Unknown")),
                            ]
                            http_response_headers = StatusAndHeaders(response_status_line, response_headers)
                            response_payload = BytesIO(response_text.encode("utf-8"))
                            response_record = writer.create_warc_record(url, "response", payload=response_payload, http_headers=http_response_headers)
                            response_record.rec_headers.add_header("WARC-Concurrent-To", request_record.rec_headers.get_header("WARC-Record-ID"))
                            response_record.rec_headers.add_header("WARC-IP-Address", ip_address)
                            writer.write_record(response_record)

                            # Metadata record
                            timestamp = datetime.now().isoformat() + "Z"
                            metadata_content = f"URL: {url}\nTimestamp: {timestamp}\nContent-Length: {len(response_text.encode('utf-8'))}\n"
                            metadata_payload = BytesIO(metadata_content.encode("utf-8"))
                            metadata_record = writer.create_warc_record(
                                f"urn:uuid:{str(uuid.uuid4())}",
                                "metadata",
                                payload=metadata_payload,
                                warc_content_type="application/warc-fields",
                            )
                            metadata_record.rec_headers.add_header("WARC-Concurrent-To", response_record.rec_headers.get_header("WARC-Record-ID"))
                            metadata_record.rec_headers.add_header("WARC-IP-Address", ip_address)
                            writer.write_record(metadata_record)
                        if update_progress:
                            update_progress(idx, total_links, f"Processed {idx}/{total_links}: {url}")


                        print(f"Saved WARC file for {url} at {warc_file_path}")
                except Exception as e:
                    print(f"Failed to fetch {url}: {e}")


