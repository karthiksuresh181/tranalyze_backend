from os import write
import re
from flask import Blueprint, request, jsonify
import json
import uuid

from src.utils.json_helper import read_json, write_json
from src.configs import ACTIVE_ALERTS_JSON, INACTIVE_ALERTS_JSON, FAVORITE_PAIRS_JSON, FAVOURITE_PAIRS_LIMIT


# define the blueprint
alerts = Blueprint(name="alerts_blueprint", import_name=__name__)

@alerts.route('/set_alert', methods=['POST'])
def set_alert():
    request_data = request.get_json(force=True)
    request_data["id"] = str(uuid.uuid4())[:8]
    active_alerts_list = read_json(ACTIVE_ALERTS_JSON)
    active_alerts_list.insert(0, request_data)
    write_json(ACTIVE_ALERTS_JSON, active_alerts_list)
    update_favourite_pairs(request_data["symbol"])
    return {}

@alerts.route('/cancel_active_alert', methods=['POST'])
def cancel_active_alert():
    request_data = request.get_json(force=True)
    active_alert_id = request_data["id"]
    active_alert_list = read_json(ACTIVE_ALERTS_JSON)

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
            del inactive_alert_list[index]
            active_alert_list.insert(0, inactive_alert)
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
    write_json(ACTIVE_ALERTS_JSON, [])
    return {}

@alerts.route('/clear_inactive_alerts', methods=['GET'])
def clear_inactive_alerts():
    write_json(INACTIVE_ALERTS_JSON, [])
    return {}

def update_favourite_pairs(symbol):
    favourite_list = read_json(FAVORITE_PAIRS_JSON)
    if not symbol in favourite_list:
        favourite_list.insert(0, symbol)
        if(len(favourite_list) > FAVOURITE_PAIRS_LIMIT): favourite_list.pop()
        write_json(FAVORITE_PAIRS_JSON, favourite_list)