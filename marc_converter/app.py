
import os
import logging
from flask import Flask
from flask_cors import CORS

# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG' if os.environ.get('DEBUG') else 'INFO').upper()
logging.basicConfig(
	level=LOG_LEVEL,
	format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger('marc_converter')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins (for dev)

# Debug mode from env
if os.environ.get('DEBUG'):
	app.config['DEBUG'] = True
	logger.info('Running in DEBUG mode')
else:
	app.config['DEBUG'] = False

# Import routes to register them with the app
import marc_converter.views
import marc_converter.api
