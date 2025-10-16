from flask import Flask
from flask_cors import CORS
CORS_origins = '*'
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins (for dev)

# Import routes to register them with the app
import marc_converter.views
import marc_converter.api
