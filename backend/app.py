import asyncio
import requests
from flask import Flask
from flask_socketio import SocketIO
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="asyncio")

# Load dataset
base_url = "https://atmos.nmsu.edu/PDS/data/jnomwr_2100/DATA/SYNCHROTRON/"

def get_csv_links():
    """Scrape site containing Synchrotron data"""
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find CSV links
    csv_links = [a["href"] for a in soup.find_all("a") if a["href"].endswith(".CSV")]
    
    if not csv_links:
        raise Exception("No CSV files found.")
    
    return [base_url + link for link in csv_links]

def download_merge_csvs():
    """Download all CSV files, merge into a single df"""
    