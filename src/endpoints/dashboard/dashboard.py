from flask import Blueprint, send_file, jsonify, request
from binance import Client
from src.utils.telegram_client import send_message_to_bot
import pandas as pd

from src.utils.json_helper import read_json
from src.utils.binance_api import *

# define the blueprint
dashboard = Blueprint(name="dashboard_blueprint", import_name=__name__)

@dashboard.route('/get_overview', methods=['GET'])
def get_overview():
    return generate_overview()




