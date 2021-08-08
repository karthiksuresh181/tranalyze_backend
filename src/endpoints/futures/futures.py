from flask import Blueprint, send_file

# define the blueprint
futures = Blueprint(name="futures_blueprint", import_name=__name__)

@futures.route('/get_coin_list', methods=['GET'])
def get_coin_list():
    return send_file("./static/resources/coin_list_futures.json")
