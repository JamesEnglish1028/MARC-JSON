#!/bin/bash
# Start the Flask development server for MARC-Converter
export FLASK_APP=marc_converter.app:app
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=10000
