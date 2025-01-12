import os
import csv

def get_token_count_from_csv(tokens_csv_path):
    """
    Extract the total token count from a tokens.csv file.
    Handles empty or invalid files gracefully.
    """
    total_tokens = 0
    if os.path.exists(tokens_csv_path):
        try:
            with open(tokens_csv_path, "r") as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip the header safely
                for row in reader:
                    if row and row[0] != "TOTAL":  # Check for valid row and skip the "TOTAL" row
                        total_tokens += int(row[1])
        except (StopIteration, ValueError) as e:
            # Log or handle errors when reading the file
            print(f"Error reading tokens.csv at {tokens_csv_path}: {e}")
    return total_tokens


def get_project_level_stats(output_root):
    """
    Calculate project-level statistics (summary for all subprojects within a project).
    """
    project_data = []

    for project in os.listdir(output_root):
        project_path = os.path.join(output_root, project)
        if os.path.isdir(project_path):
            total_files = 0
            total_tokens = 0
            total_bytes = 0

            for subproject in os.listdir(project_path):
                subproject_path = os.path.join(project_path, subproject)
                if os.path.isdir(subproject_path):
                    # PDFs
                    pdf_folder = os.path.join(subproject_path, "pdfs", "scraped-pdfs")
                    if os.path.exists(pdf_folder):
                        for pdf_file in os.listdir(pdf_folder):
                            if pdf_file.endswith(".pdf"):
                                total_files += 1
                                total_bytes += os.path.getsize(os.path.join(pdf_folder, pdf_file))

                    # WARCs
                    warc_folder = os.path.join(subproject_path, "warcs", "scraped-warcs")
                    if os.path.exists(warc_folder):
                        for warc_file in os.listdir(warc_folder):
                            if warc_file.endswith(".warc"):
                                total_files += 1
                                total_bytes += os.path.getsize(os.path.join(warc_folder, warc_file))

                    # Tokens
                    tokens_csv_path = os.path.join(subproject_path, "tokens", "tokens.csv")
                    total_tokens += get_token_count_from_csv(tokens_csv_path)

            # Add a row summarizing the project
            project_data.append([project, total_files, total_tokens, total_bytes])

    return project_data

def get_subproject_level_stats(output_root):
    """
    Calculate subproject-level statistics (details for each subproject).
    """
    subproject_data = []

    for project in os.listdir(output_root):
        project_path = os.path.join(output_root, project)
        if os.path.isdir(project_path):
            for subproject in os.listdir(project_path):
                subproject_path = os.path.join(project_path, subproject)
                if os.path.isdir(subproject_path):
                    total_files = 0
                    total_tokens = 0
                    total_bytes = 0

                    # PDFs
                    pdf_folder = os.path.join(subproject_path, "pdfs", "scraped-pdfs")
                    if os.path.exists(pdf_folder):
                        for pdf_file in os.listdir(pdf_folder):
                            if pdf_file.endswith(".pdf"):
                                total_files += 1
                                total_bytes += os.path.getsize(os.path.join(pdf_folder, pdf_file))

                    # WARCs
                    warc_folder = os.path.join(subproject_path, "warcs", "scraped-warcs")
                    if os.path.exists(warc_folder):
                        for warc_file in os.listdir(warc_folder):
                            if warc_file.endswith(".warc"):
                                total_files += 1
                                total_bytes += os.path.getsize(os.path.join(warc_folder, warc_file))

                    # Tokens
                    tokens_csv_path = os.path.join(subproject_path, "tokens", "tokens.csv")
                    total_tokens += get_token_count_from_csv(tokens_csv_path)

                    # Add a row for the subproject
                    subproject_data.append([project, subproject, total_files, total_tokens, total_bytes])

    return subproject_data
