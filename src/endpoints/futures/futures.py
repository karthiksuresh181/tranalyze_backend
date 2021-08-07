from flask import Blueprint
import os

import numpy as np

# define the blueprint
futures = Blueprint(name="alerts_blueprint", import_name=__name__)

@futures.route('/get_all_coin_list', methods=['GET'])
def hello_world_2():
    return "Hello world 2"
