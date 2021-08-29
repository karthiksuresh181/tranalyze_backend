from flask import Blueprint, request, jsonify
import uuid
from binance import ThreadedWebsocketManager
from functools import partial
from numpy import add
import requests

from src.utils.json_helper import read_json, write_json
from src.configs import ACTIVE_ALERTS_JSON, INACTIVE_ALERTS_JSON, FAVORITE_PAIRS_JSON, FAVOURITE_PAIRS_LIMIT
from src.utils.email_client import send_email
from src.utils.telegram_client import send_message_to_bot

bsm = ThreadedWebsocketManager()
bsm.start()

sockets = {}

# define the blueprint
alerts = Blueprint(name="alerts_blueprint", import_name=__name__)

@alerts.route('/set_alert', methods=['POST'])
def set_alert():
    request_data = request.get_json(force=True)
    alert_id = str(uuid.uuid4())[:8]
    symbol = request_data["symbol"]
    alert_price = float(request_data["price"])
    open_alert_socket(alert_id, symbol, alert_price)
    request_data["id"] = alert_id
    add_alert_to_json(request_data)
    update_favourite_pairs(request_data["symbol"])
    return {}

@alerts.route('/cancel_active_alert', methods=['POST'])
def cancel_active_alert():
    request_data = request.get_json(force=True)
    active_alert_id = request_data["id"]
    active_alert_list = read_json(ACTIVE_ALERTS_JSON)
    close_alert_socket(active_alert_id)
    for index ,alert in enumerate(active_alert_list):
        if(alert["id"] == active_alert_id):
            del active_alert_list[index]
            write_json(ACTIVE_ALERTS_JSON, active_alert_list)
            return {}
    return {}

@alerts.route('/activate_inactive_alert', methods=['POST'])
def activate_inactive_alert():
    request_data = request.get_json(force=True)
    inactive_alert_id = request_data["id"]
    active_alert_list = read_json(ACTIVE_ALERTS_JSON)
    inactive_alert_list = read_json(INACTIVE_ALERTS_JSON)
    for index, alert in enumerate(inactive_alert_list):
        if(alert["id"] == inactive_alert_id):
            inactive_alert = alert.copy()
            inactive_alert_symbol = inactive_alert["symbol"]
            inactive_alert_id = inactive_alert["id"]
            inactive_alert_price = float(inactive_alert["price"])
            del inactive_alert_list[index]
            active_alert_list.insert(0, inactive_alert)
            open_alert_socket(inactive_alert_id, inactive_alert_symbol, inactive_alert_price)
            write_json(ACTIVE_ALERTS_JSON, active_alert_list)
            write_json(INACTIVE_ALERTS_JSON, inactive_alert_list)
            return {}
    return {}

@alerts.route('/get_active_alerts', methods=['GET'])
def get_active_alerts():
    active_alert_list = read_json(ACTIVE_ALERTS_JSON)
    return jsonify(active_alert_list)

@alerts.route('/get_inactive_alerts', methods=['GET'])
def get_inactive_alerts():
    inactive_alert_list = read_json(INACTIVE_ALERTS_JSON)
    return jsonify(inactive_alert_list)

@alerts.route('/cancel_active_alerts', methods=['GET'])
def cancel_active_alerts():
    active_alert_list = read_json(ACTIVE_ALERTS_JSON)
    for alert in active_alert_list:
        close_alert_socket(alert["id"])
    write_json(ACTIVE_ALERTS_JSON, [])
    return {}

@alerts.route('/clear_inactive_alerts', methods=['GET'])
def clear_inactive_alerts():
    write_json(INACTIVE_ALERTS_JSON, [])
    return {}

@alerts.route("/test_alert", methods=['GET'])
def test_alert():
    print(sockets)
    return {}

def get_alert_direction(symbol, alert_price):
    current_price = float(get_current_price(symbol))
    alert_direction = "lesser"
    if(current_price > alert_price): alert_direction = "greater"
    return alert_direction

def get_current_price(symbol):
    r = requests.get(f"https://www.binance.com/fapi/v1/ticker/price?symbol={symbol}")
    return (r.json()["price"])

def alert_callback(msg, alert_price, alert_direction, alert_id):
    current_price = float(msg['data']['a'])
    symbol = msg['data']['s']
    stop_alert = False
    if(alert_direction == "lesser"):
        if current_price >= alert_price:
            stop_alert = True
    else:
        if current_price <= alert_price:
            stop_alert = True
    if(stop_alert):
        close_alert_socket(alert_id)
        push_to_inactive_alerts(alert_id)
        send_email(symbol, str(current_price))
        send_message_to_bot(symbol, current_price)
        return

def open_alert_socket(alert_id, symbol, alert_price):
    alert_direction = get_alert_direction(symbol, alert_price)
    sockets[alert_id] = bsm.start_symbol_ticker_futures_socket(callback=partial(alert_callback, alert_price=alert_price, alert_direction=alert_direction, alert_id=alert_id), symbol=symbol)

def close_alert_socket(alert_id):
    bsm.stop_socket(sockets[alert_id])
    del sockets[alert_id]

def add_alert_to_json(request_data):
    active_alert_list = read_json(ACTIVE_ALERTS_JSON)
    active_alert_list.insert(0, request_data)
    write_json(ACTIVE_ALERTS_JSON, active_alert_list)

def push_to_inactive_alerts(alert_id):
    active_alert_list = read_json(ACTIVE_ALERTS_JSON)
    inactive_alert_list = read_json(INACTIVE_ALERTS_JSON)
    for index, alert in enumerate(active_alert_list):
        if(alert["id"] == alert_id):
            active_alert = alert.copy()
            del active_alert_list[index]
            inactive_alert_list.insert(0, active_alert)
            write_json(ACTIVE_ALERTS_JSON, active_alert_list)
            write_json(INACTIVE_ALERTS_JSON, inactive_alert_list)
            return {}

def update_favourite_pairs(symbol):
    favourite_list = read_json(FAVORITE_PAIRS_JSON)
    if not symbol in favourite_list:
        favourite_list.insert(0, symbol)
        if(len(favourite_list) > FAVOURITE_PAIRS_LIMIT): favourite_list.pop()
        write_json(FAVORITE_PAIRS_JSON, favourite_list)