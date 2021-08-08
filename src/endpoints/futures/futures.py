from flask import Blueprint, send_file, jsonify

from src.utils.json_helper import read_json
from src.configs import FAVORITE_PAIRS_JSON

# define the blueprint
futures = Blueprint(name="futures_blueprint", import_name=__name__)

@futures.route('/get_coin_list', methods=['GET'])
def get_coin_list():
    return send_file("./static/resources/coin_list_futures.json")

@futures.route('/get_favourite_pairs', methods=['GET'])
def get_favourites_list():
    favourite_list = read_json(FAVORITE_PAIRS_JSON)
    return jsonify(favourite_list)