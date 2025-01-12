# Scrape Automation and Token Estimator

This is a powerful **Streamlit-based application** designed for managing scraping workflows, token estimation, and file compression. It provides a structured approach to managing projects and subprojects, allowing users to scrape, process, and analyze data efficiently.

---

## **Features**

- **Dynamic Project and Subproject Management**:
  - Create, manage, and navigate projects and their subprojects.
  - View a structured tree of projects and subprojects in real-time.

- **Scraping Tools**:
  - **Link Scraper**: Extract links from websites using predefined or custom strategies.
  - **PDF Scraper**: Download and process PDFs from scraped links.
  - **WARC Scraper**: Save web pages as WARC files for archival purposes.

- **Token Estimation**:
  - Count tokens in PDFs and WARC files, with optional CSS selector-based extraction for focused processing.

- **File Compression**:
  - Compress PDFs into `.zip` files and WARC files into `.warc.gz` files for storage optimization.

- **Dashboard**:
  - View a comprehensive overview of project-level and subproject-level statistics, including file counts, token counts, and total size in bytes.

---

## **Installation**

### 1. Clone the Repository
First, clone the repository to your local machine:
```bash
git clone https://github.com/your-repo-url.git
cd project_directory
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment to ensure dependency isolation:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required dependencies from the requirements.txt file:

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
Start the Streamlit app:

```bash
streamlit run app.py
```

---

## **Usage**

### 1. Starting the App
Once the app starts, you will see a sidebar for managing projects and subprojects, and several feature tabs to navigate through.

### 2. Managing Projects and Subprojects
Before using any other features, you must first create a project and its subprojects:

- Navigate to the sidebar under the Project Management section.
- Click the "Add New Project" button to unlock the input field.
- Enter the project name (e.g., kominfo) and click Save New Project.
- Cancel the input section by clicking Cancel New Project.
- Select the newly created project from the dropdown.

Once a project is selected:

- Click "Add New Subproject" to unlock the input field.
- Enter subproject names (e.g., news, regulations, information) one by one, saving each.
- Select a subproject using the dropdown.

### 3. Unlocking Features
Once a project and subproject are selected, you can unlock other features:

- **Link Scraper**: Scrape links from websites and save them to a .csv file.
- **PDF Scraper**: Download PDFs from scraped links and process them.
- **WARC Scraper**: Save web pages as .warc files for archival purposes.
- **Token Estimator**: Estimate token counts in PDFs and WARC files.
- **Compressor**: Compress files into .zip and .warc.gz formats.

---

## **Example Workflow**

Here’s a sample workflow for scraping data from the Kominfo website:

1. **Create a Project**: Add `kominfo` as a project.
2. **Add Subprojects**:
   - Add `news`, `regulations`, and `information` as subprojects under `kominfo`.
3. **Use Link Scraper**:
   - Scrape links from the news section of the Kominfo website.
   - Save the extracted links to `output/kominfo/news/links/links.csv`.
4. **Scrape PDFs and WARCs**:
   - Download PDFs from the scraped links into `output/kominfo/news/pdfs/scraped-pdfs/`.
   - Save web pages as `.warc` files into `output/kominfo/news/warcs/scraped-warcs/`.
5. **Estimate Tokens**:
   - Count tokens in the PDFs and WARCs for the news subproject.
6. **Compress Files**:
   - Compress the PDFs and WARCs for storage optimization.

---

## **Folder Structure**

The application dynamically creates the following folder structure during runtime:

```
output/
└── <project_name>/
    └── <subproject_name>/
        ├── pdfs/
        │   └── scraped-pdfs/
        ├── links/
        ├── warcs/
        │   └── scraped-warcs/
        ├── tokens/
        └── compressed/
```

- `pdfs/scraped-pdfs/`: Stores downloaded PDFs.
- `links/`: Contains .csv files with scraped links.
- `warcs/scraped-warcs/`: Contains `.warc` files for archived web pages.
- `tokens/`: Contains token counts in `.csv` format.
- `compressed/`: Contains compressed `.zip` and `.warc.gz` files.

---

## **System Requirements**

- **Python**: Version 3.8 or later
- **Google Chrome**: Installed
- **ChromeDriver**: Compatible with your Chrome version

[Download ChromeDriver](https://sites.google.com/chromium.org/driver/)

---

## **Contributing**

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Make your changes and commit:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push your changes:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## **License**

This project is licensed under the MIT License.

---

## **Contact**

For questions or support, please contact:

- **Email**: your-email@example.com
- **GitHub**: [Your GitHub Profile](https://github.com/your-profile)
