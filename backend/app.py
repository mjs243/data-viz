import asyncio
from flask import Flask
from flask_socketio import SocketIO
import pandas as pd
import numpy as np

app = Flask(__name__)
socketio = SocketIO(app)