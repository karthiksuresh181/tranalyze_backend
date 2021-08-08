import re
from flask import Blueprint, request, jsonify
import json
import uuid

from src.configs import ACTIVE_ALERTS_JSON, INACTIVE_ALERTS_JSON


# define the blueprint
alerts = Blueprint(name="alerts_blueprint", import_name=__name__)

@alerts.route('/set_alert', methods=['POST'])
def set_alert():
    request_data = request.get_json(force=True)
    request_data["id"] = str(uuid.uuid4())[:8]
    active_alerts_list = read_active_alert_json()
    active_alerts_list.insert(0, request_data)
    write_active_alert_json(active_alerts_list)
    return {}

@alerts.route('/cancel_active_alert', methods=['POST'])
def cancel_active_alert():
    request_data = request.get_json(force=True)
    active_alert_id = request_data["id"]
    active_alert_list = read_active_alert_json()

    for index ,alert in enumerate(active_alert_list):
        if(alert["id"] == active_alert_id):
            del active_alert_list[index]
            write_active_alert_json(active_alert_list)
            return {}
    return {}

@alerts.route('/activate_inactive_alert', methods=['POST'])
def activate_inactive_alert():
    request_data = request.get_json(force=True)
    inactive_alert_id = request_data["id"]
    active_alert_list = read_active_alert_json()
    inactive_alert_list = read_inactive_alert_json()

    for index, alert in enumerate(inactive_alert_list):
        if(alert["id"] == inactive_alert_id):
            inactive_alert = alert.copy()
            del inactive_alert_list[index]
            active_alert_list.insert(0, inactive_alert)
            write_active_alert_json(active_alert_list)
            write_inactive_alert_json(inactive_alert_list)
            return {}
    return {}

@alerts.route('/get_active_alerts', methods=['GET'])
def get_active_alerts():
    json_data = read_active_alert_json()
    return jsonify(json_data)

@alerts.route('/get_inactive_alerts', methods=['GET'])
def get_inactive_alerts():
    json_data = read_inactive_alert_json()
    return jsonify(json_data)

def read_active_alert_json():
    with open(ACTIVE_ALERTS_JSON)as f:
        json_data = json.load(f)
    return json_data

def read_inactive_alert_json():
    with open(INACTIVE_ALERTS_JSON)as f:
        json_data = json.load(f)
    return json_data

def write_active_alert_json(json_data):
    with open(ACTIVE_ALERTS_JSON, "w")as f:        
        json.dump(json_data, f)

def write_inactive_alert_json(json_data):
    with open(INACTIVE_ALERTS_JSON, "w")as f:        
        json.dump(json_data, f)