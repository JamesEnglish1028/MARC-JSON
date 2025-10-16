# API endpoints for the Flask app


import os
from flask import request, jsonify
from marc_converter.app import app
from marc_converter.logic import process_marc_file_upload, process_marc_url_api

def check_token():
    required_token = os.environ.get('API_TOKEN')
    if required_token:
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return False
        token = auth.split(' ', 1)[1]
        if token != required_token:
            return False
    return True

@app.route('/api/convert', methods=['POST'])
def api_convert():
    if not check_token():
        return jsonify({'error': 'Unauthorized'}), 401
    # Accept file upload
    if 'file' in request.files:
        file = request.files['file']
        return process_marc_file_upload(file)
    # Accept JSON with URL
    if request.is_json:
        data = request.get_json()
        marc_url = data.get('url')
        if marc_url:
            return process_marc_url_api(marc_url)
        else:
            return jsonify({'error': 'No url provided'}), 400
    return jsonify({'error': 'No file or url provided'}), 400
