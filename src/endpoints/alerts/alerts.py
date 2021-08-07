from flask import Blueprint
import os

import numpy as np

# define the blueprint
alerts = Blueprint(name="alerts_blueprint", import_name=__name__)

@alerts.route('/init_2', methods=['GET'])
def hello_world_2():
    return "Hello world 2"
