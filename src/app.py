from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import sys

# load modules
from src.endpoints.alerts.alerts import alerts
from src.endpoints.futures.futures import futures

# init Flask app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = "Content-Type"

# register blueprints. ensure that all paths are versioned!
app.register_blueprint(alerts, url_prefix="/api/v1/alerts")
app.register_blueprint(futures, url_prefix="/api/v1/futures")
