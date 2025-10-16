# Views for the Flask app

from flask import render_template_string, request, send_file
from marc_converter.app import app
from marc_converter.logic import process_marc_url

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Palace MARC File to Inventory Spreadsheet Converter</title>
    <!-- ...existing HTML/CSS/JS... -->
</head>
<body>
    <!-- ...existing HTML... -->
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        marc_url = request.form['marc_url']
        fmt = request.form['format']
        return process_marc_url(marc_url, fmt)
    return render_template_string(HTML_FORM)
