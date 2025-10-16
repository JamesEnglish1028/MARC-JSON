# API endpoints for the Flask app


import os

import logging
from flask import request, jsonify
from marc_converter.app import app, logger
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
    logger.info(f"/api/convert called. Method: {request.method}, Content-Type: {request.content_type}")
    try:
        if not check_token():
            logger.warning("Unauthorized API access attempt.")
            return jsonify({'error': 'Unauthorized'}), 401
        fmt = request.args.get('format', 'json').lower()
        # Accept file upload
        logger.info(f"Request.files keys: {list(request.files.keys())}")
        if 'file' in request.files:
            file = request.files['file']
            logger.info(f"File upload received: filename={getattr(file, 'filename', None)}, content_type={getattr(file, 'content_type', None)}, content_length={getattr(file, 'content_length', None)}")
            if not file or not getattr(file, 'filename', None):
                logger.error("File object is None or missing filename.")
                return jsonify({'error': 'No file uploaded or filename missing'}), 400
            try:
                return process_marc_file_upload(file, fmt)
            except Exception as e:
                logger.exception(f"Error in process_marc_file_upload: {e}")
                return jsonify({'error': f'File upload failed: {str(e)}'}), 500
        # Accept JSON with URL
        if request.is_json:
            data = request.get_json()
            marc_url = data.get('url')
            logger.info(f"URL ingestion request: {marc_url}")
            if marc_url:
                return process_marc_url_api(marc_url, fmt)
            else:
                logger.error("No url provided in JSON body.")
                return jsonify({'error': 'No url provided'}), 400
        logger.error("No file or url provided in request.")
        return jsonify({'error': 'No file or url provided'}), 400
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        logger.exception(f"Unhandled exception in /api/convert: {e}")
        # In debug mode, return error details and logs
        if app.config.get('DEBUG'):
            return jsonify({
                'error': str(e),
                'exception': repr(e),
                'traceback': tb_str
            }), 500
        return jsonify({'error': 'Internal server error'}), 500
