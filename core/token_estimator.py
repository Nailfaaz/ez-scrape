import os
import gzip
import csv
import logging
from tqdm import tqdm
from bs4 import BeautifulSoup
from langdetect import detect
from warcio.archiveiterator import ArchiveIterator
import fitz  # PyMuPDF for PDF handling

class TokenEstimator:
    def __init__(self, project_folder, log_callback=None):
        """
        Initialize the TokenEstimator with project folder setup and logging.
        """
        self.project_folder = project_folder
        self.log_callback = log_callback or (lambda msg: None)

        # Directories for output
        self.logs_folder = os.path.join(self.project_folder, "tokens", "logs")
        self.tokens_folder = os.path.join(self.project_folder, "tokens")

        os.makedirs(self.logs_folder, exist_ok=True)
        os.makedirs(self.tokens_folder, exist_ok=True)

        # Configure logger
        self.logger = logging.getLogger("TokenEstimator")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            log_file = os.path.join(self.logs_folder, "token_estimator.log")
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

    def count_tokens_in_text(self, text):
        """
        Estimate token count from the given text.
        """
        cleaned_text = "".join(text.split())  # Remove whitespace
        return len(cleaned_text) // 4

    def count_tokens_in_pdf(self, pdf_path):
        """
        Count tokens in a PDF file.
        """
        try:
            pdf_document = fitz.open(pdf_path)
            total_characters = 0

            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                total_characters += len(text)

            pdf_document.close()
            tokens = total_characters // 4
            return total_characters, tokens
        except Exception as e:
            self._log(f"Error processing PDF {pdf_path}: {e}")
            raise

    def extract_text_from_html(self, html_content):
        """
        Extract text from HTML content using BeautifulSoup.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator=" ")

    def count_tokens_in_single_warc(self, warc_path, use_css_selector=False, css_selector=None):
        """
        Count tokens in a single WARC file.
        """
        total_tokens = 0
        records_count = 0

        try:
            with open(warc_path, "rb") as stream:
                for record in ArchiveIterator(stream):
                    if record.rec_type == "response":
                        html_content = record.content_stream().read()
                        if use_css_selector:
                            if not css_selector:
                                raise ValueError("CSS selector must be provided for tag-based extraction.")
                            soup = BeautifulSoup(html_content, "html.parser")
                            target_elements = soup.select(css_selector)
                            for element in target_elements:
                                text = element.get_text(separator=" ", strip=True)
                                total_tokens += self.count_tokens_in_text(text)
                        else:
                            text_content = self.extract_text_from_html(html_content)
                            language = detect(text_content) if text_content.strip() else "unknown"
                            if language == "id":
                                total_tokens += self.count_tokens_in_text(text_content)

                        records_count += 1

            self._log(f"Processed {records_count} records from {warc_path}: {total_tokens} tokens")
            return total_tokens
        except Exception as e:
            self._log(f"Error processing WARC {warc_path}: {e}")
            return 0

    def process_pdfs(self, pdf_folder, update_progress=None):
        """
        Process PDFs and count tokens.
        """
        pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
        csv_path = os.path.join(self.tokens_folder, "tokens.csv") 

        self._log(f"Found {len(pdf_files)} PDF files in {pdf_folder}")

        total_tokens = 0

        with open(csv_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["file", "token_count"])

            for idx, pdf_file in enumerate(tqdm(pdf_files, desc="Processing PDFs", leave=True), start=1):
                pdf_path = os.path.join(pdf_folder, pdf_file)
                try:
                    _, token_count = self.count_tokens_in_pdf(pdf_path)
                    csv_writer.writerow([pdf_file, token_count])
                    total_tokens += token_count

                    if update_progress:
                        update_progress(idx, len(pdf_files), f"Processed {idx}/{len(pdf_files)} PDFs")
                except Exception as e:
                    self._log(f"Failed to process PDF {pdf_file}: {e}")

            # Write total tokens at the end of the CSV
            csv_writer.writerow(["TOTAL (PDFs)", total_tokens])

        self._log(f"Completed processing PDFs. Total tokens: {total_tokens}")

    def process_warcs(self, warc_folder, use_css_selector=False, css_selector=None, update_progress=None):
        """
        Process WARC files and count tokens.

        If a CSS selector is provided, it extracts text based on the selector.
        Otherwise, processes all text in the HTML.
        """
        warc_files = [f for f in os.listdir(warc_folder) if f.endswith(".warc")]
        csv_path = os.path.join(self.tokens_folder, "tokens.csv")

        self._log(f"Found {len(warc_files)} WARC files in {warc_folder}")

        total_tokens = 0

        with open(csv_path, "a", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["file", "token_count"])

            for idx, warc_file in enumerate(tqdm(warc_files, desc="Processing WARCs"), start=1):
                warc_file_path = os.path.join(warc_folder, warc_file)
                try:
                    file_token_count = self.count_tokens_in_single_warc(
                        warc_file_path, use_css_selector, css_selector
                    )
                    csv_writer.writerow([warc_file, file_token_count])
                    total_tokens += file_token_count

                    if update_progress:
                        update_progress(idx, len(warc_files), f"Processed {idx}/{len(warc_files)} WARCs")
                except Exception as e:
                    self._log(f"Failed to process WARC {warc_file}: {e}")

            # Write total tokens for WARCs
            csv_writer.writerow(["TOTAL (WARCs)", total_tokens])

        self._log(f"Completed processing WARCs. Total tokens: {total_tokens}")

