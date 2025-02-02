import os
import streamlit as st
from resources.config import OUTPUT_ROOT
from ui.project_management import project_management_sidebar
from ui.link_scraper_tab import link_scraper_tab
from ui.warc_scraper_tab import warc_scraper_tab
from ui.pdf_scraper_tab import pdf_scraper_tab
from ui.token_estimator_tab import token_estimator_tab
from ui.compress_tab import compress_tab
from ui.dashboard_tab import dashboard_tab
from ui.custom_link_scraper_tab import custom_link_scraper_tab

# Fix asyncio issue on Windows
import sys
import asyncio
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Ensure output directory exists
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# Initialize Streamlit session state
if "current_project" not in st.session_state:
    st.session_state["current_project"] = None
if "current_subproject" not in st.session_state:
    st.session_state["current_subproject"] = None

# Streamlit app
st.title("Scrape Automation and Token Estimator")

# Sidebar for Project Management
with st.sidebar:
    project_management_sidebar(OUTPUT_ROOT)

# Tabs for Features
tabs = st.tabs(["Link Scraper", "WARC Scraper", "PDF Scraper", "Token Estimator", "Compressor", "Dashboard", "Custom Link Scraper", "Other Features (Coming Soon)"]) 

# Link Scraper Tab
with tabs[0]:
    link_scraper_tab(OUTPUT_ROOT)

# WARC Scraper Tab
with tabs[1]:
    warc_scraper_tab(OUTPUT_ROOT)

# PDF Scraper Tab
with tabs[2]:
    pdf_scraper_tab(OUTPUT_ROOT)

# Token Estimator Tab
with tabs[3]:
    token_estimator_tab(OUTPUT_ROOT)

# Compression Tab
with tabs[4]:
    compress_tab(OUTPUT_ROOT)

# Dashboard Tab
with tabs[5]:
    dashboard_tab(OUTPUT_ROOT)

# Custom Link Scraper Tab
with tabs[6]:
    custom_link_scraper_tab()

# Placeholder for other features
with tabs[7]:
    st.write("Other features coming soon...")

