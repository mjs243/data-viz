import asyncio
import requests
import aiohttp
import os
from io import StringIO
from flask import Flask
from flask_socketio import SocketIO
import sqlite3
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load dataset
base_url = "https://atmos.nmsu.edu/PDS/data/jnomwr_2100/DATA/SYNCHROTRON/"
db_path = "backend/data/synchrotron_data.db"

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
        
def if_data_exists(file_name):
    """Check if data already exists in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM synchrotron_data WHERE file_name=?", (file_name,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists

async def download_merge_csvs(file_url):
    """Download all CSV files, merge into a single df"""
    file_name = os.path.basename(file_url)
    if if_data_exists(file_name):
        print(f"Skipping cached file: {file_name}")
        return None  # Data already exists, skip download
    
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                content = await response.text()
                df = pd.read_csv(StringIO(content))

                if "t_ephem_time" in df.columns:
                    df['timestamp'] = pd.to_datetime(df['t_ephem_time'], unit='s')

                store_data(df, file_name)
                print(f"Downloaded and stored {file_name}")

def store_data(df, file_name):
    """Store data in the SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("INSERT INTO synchrotron_data (timestamp, antenna_temp, file_name) VALUES (?, ?, ?)",
                        (row["timestamp"].isoformat(), row["ant_temp_synchrotron"], file_name))
        
    conn.commit()
    conn.close()

async def download_all_csvs():
    """Download all CSV files in parallel"""
    csv_links = await fetch_csv_links()
    tasks = [download_merge_csvs(link) for link in csv_links]
    await asyncio.gather(*tasks)

async def stream_data():
    """Stream dataset row by row via websocket"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, antenna_temp FROM synchrotron_data ORDER BY timestamp ASC")

    for row in cursor.fetchall():
        socketio.emit('data', {'timestamp': row[0], 'antenna_temp': row[1]})
        await asyncio.sleep(0.1)

    conn.close()

def start_background_tasks():
    """Start background tasks"""
    asyncio.create_task(download_all_csvs())
    asyncio.create_task(stream_data())

@app.route('/')
def index():
    return "Welcome to the Synchrotron Data API!"

if __name__ == "__main__":
    create_db()
    socketio.on_event("connect", start_background_tasks)
    # socketio.start_background_task(download_all_csvs)
    # socketio.start_background_task(stream_data)
    socketio.run(app, host='0.0.0.0', port=3000, allow_unsafe_werkzeug=True)