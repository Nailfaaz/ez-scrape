import os
import zipfile
import gzip
import shutil
import logging
import csv


class FileCompressor:
    def __init__(self, project_folder, project_name, subproject_name):
        """
        Initialize the FileCompressor with the project and subproject context.
        """
        self.project_folder = project_folder
        self.project_name = project_name
        self.subproject_name = subproject_name
        self.compressed_folder = os.path.join(self.project_folder, "compressed")
        self.bytes_csv_path = os.path.join(self.compressed_folder, "bytes.csv")
        
        # Ensure the compressed folder exists
        os.makedirs(self.compressed_folder, exist_ok=True)

        # Configure logging
        self.logger = logging.getLogger("FileCompressor")
        self.logger.setLevel(logging.INFO)
        log_file = os.path.join(self.compressed_folder, "compression.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(file_handler)

    def _log(self, message):
        """
        Log messages to file.
        """
        self.logger.info(message)

    def compress_pdfs(self):
        """
        Compress all PDFs in <project>/<subproject>/pdfs/scraped-pdfs/ into a ZIP file.
        """
        pdf_dir = os.path.join(self.project_folder, "pdfs", "scraped-pdfs")
        zip_file_name = f"{self.project_name}_{self.subproject_name}.zip"
        zip_path = os.path.join(self.compressed_folder, zip_file_name)

        file_sizes = []
        total_bytes = 0

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for pdf_file in os.listdir(pdf_dir):
                    if pdf_file.endswith(".pdf"):
                        pdf_path = os.path.join(pdf_dir, pdf_file)
                        file_size = os.path.getsize(pdf_path)
                        zipf.write(pdf_path, arcname=pdf_file)
                        file_sizes.append((pdf_file, file_size))
                        total_bytes += file_size
                        self._log(f"Added {pdf_file} ({file_size} bytes) to ZIP archive.")

            file_sizes.append(("TOTAL", total_bytes))
            self._write_bytes_to_csv(file_sizes)

            self._log(f"ZIP archive created: {zip_path} ({total_bytes} bytes)")
            return zip_path
        except Exception as e:
            self._log(f"Error compressing PDFs: {e}")
            return None

    def compress_warcs(self):
        """
        Compress all WARCs in <project>/<subproject>/warcs/scraped-warcs/ into a .warc.gz file.
        """
        warc_dir = os.path.join(self.project_folder, "warcs", "scraped-warcs")
        gz_file_name = f"{self.project_name}_{self.subproject_name}.warc.gz"
        gz_path = os.path.join(self.compressed_folder, gz_file_name)

        file_sizes = []
        total_bytes = 0

        try:
            with gzip.open(gz_path, 'wb') as gz_file:
                for warc_file in os.listdir(warc_dir):
                    if warc_file.endswith(".warc"):
                        warc_path = os.path.join(warc_dir, warc_file)
                        file_size = os.path.getsize(warc_path)
                        with open(warc_path, 'rb') as warc:
                            shutil.copyfileobj(warc, gz_file)
                        file_sizes.append((warc_file, file_size))
                        total_bytes += file_size
                        self._log(f"Added {warc_file} ({file_size} bytes) to WARC.GZ archive.")

            file_sizes.append(("TOTAL", total_bytes))
            self._write_bytes_to_csv(file_sizes)

            self._log(f"WARC.GZ archive created: {gz_path} ({total_bytes} bytes)")
            return gz_path
        except Exception as e:
            self._log(f"Error compressing WARCs: {e}")
            return None

    def _write_bytes_to_csv(self, file_sizes):
        """
        Write file sizes to a unified bytes.csv.
        """
        with open(self.bytes_csv_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["file", "byte_count"])
            csv_writer.writerows(file_sizes)
