from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import sys

# load modules
from src.endpoints.dashboard.dashboard import dashboard

# init Flask app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = "Content-Type"

# register blueprints. ensure that all paths are versioned!
app.register_blueprint(dashboard, url_prefix="/api/v1/dashboard")