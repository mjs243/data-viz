import asyncio
import requests
import aiohttp
import os
from flask import Flask
from flask_socketio import SocketIO
import sqlite3
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="asyncio")

# Load dataset
base_url = "https://atmos.nmsu.edu/PDS/data/jnomwr_2100/DATA/SYNCHROTRON/"
db_path = "data/synchrotron_data.db"

# Create SQLite database and table if not exists
def create_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS synchrotron_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            antenna_temp REAL,
            file_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

async def fetch_csv_links():
    """Scrape NASA site fire Synchrotron data"""
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
    csv_links = [a['href'] for a in soup.find_all('a') if a['href'].endswith('.CSV')]
    return [base_url + link for link in csv_links]
        

def download_merge_csvs():
    """Download all CSV files, merge into a single df"""
    