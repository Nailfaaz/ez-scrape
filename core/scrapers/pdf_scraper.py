import os
import csv
import time
import logging
from selenium import webdriver


def setup_webdriver(output_folder):
    """
    Set up the WebDriver with the specified download directory.
    """
    output_folder = os.path.abspath(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": output_folder,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=options)


def wait_for_download(path, max_wait_time=300):
    """
    Wait for all downloads to complete in the specified directory.
    """
    start_time = time.time()
    while True:
        downloading = any(file.endswith(".crdownload") for file in os.listdir(path))
        if not downloading:
            break
        if time.time() - start_time > max_wait_time:
            logging.warning("Download timeout occurred.")
            break
        time.sleep(2)


def scrape_from_list(link_list, output_folder, update_progress=None):
    """
    Visit each link in the list and trigger downloads.
    """
    driver = setup_webdriver(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    total_links = len(link_list)
    for idx, link in enumerate(link_list):
        try:
            driver.get(link)
            logging.info(f"{idx + 1}/{total_links} - Downloading PDF from {link}")

            time.sleep(2)  # Allow time for download to start

            # Update progress
            if update_progress:
                update_progress(idx + 1, total_links, f"Downloading {idx + 1}/{total_links} PDFs...")
        except Exception as e:
            logging.error(f"Failed to download PDF from {link}: {e}")

    wait_for_download(output_folder)
    driver.quit()

def pdf_scraper_main(csv_path, project_folder, update_progress=None, log_callback=None):
    """
    Main function to scrape PDFs from links in a CSV file.
    """
    # Configure log file
    logs_folder = os.path.join(project_folder, "pdfs", "logs")
    os.makedirs(logs_folder, exist_ok=True)
    log_file = os.path.join(logs_folder, "pdf_scraper.log")

    # Explicitly configure logging
    logger = logging.getLogger("PDFScraper")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)

    # Log startup message
    logger.info("PDF Scraper started.")

    # Configure output folder for PDFs
    pdf_output_folder = os.path.join(project_folder, "pdfs", "scraped-pdfs")
    os.makedirs(pdf_output_folder, exist_ok=True)

    # Read links from the CSV file
    try:
        with open(csv_path, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            link_list = [row[0] for row in reader]
    except Exception as e:
        logger.error(f"Failed to read CSV file: {e}")
        raise

    # Log total links
    logger.info(f"Total links to process: {len(link_list)}")

    # Scrape PDFs
    try:
        scrape_from_list(link_list=link_list, output_folder=pdf_output_folder, update_progress=update_progress)
    except Exception as e:
        logger.error(f"Error during PDF scraping: {e}")
        raise

    # Log completion message
    logger.info("PDF Scraper completed.")
    if log_callback:
        log_callback("PDF download completed.")


