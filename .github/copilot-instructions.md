# Copilot Instructions for MARC-Converter

## Project Overview
- **Purpose:** Converts MARC records (from The Palace Project endpoint) into KBART-style inventory files (TSV, XLSX, or CSV).
- **Main Entry:** `Web_app_New.py` (Flask app, Python)
- **Input:** User selects collections; app fetches MARC records via HTTP.
- **Output:** KBART-style records in user-selected format.

## Key Files
- `Web_app_New.py`: Main Flask application, handles UI, MARC fetching, parsing, and file output.
- `README.md`: High-level project description and usage context.

## Architecture & Data Flow
- User interacts with Flask web UI to select collections and output format.
- App fetches MARC records from The Palace Project endpoint.
- MARC records are parsed and mapped to KBART fields.
- Output is generated in TSV, XLSX, or CSV as selected by the user.
- The app also exposes an API endpoint for programmatic conversion:
		- `POST /api/convert`: Accepts a MARC file upload (`file` in form-data), returns parsed MARC records as JSON. Example usage:
			```bash
			curl -F "file=@yourfile.mrc" http://localhost:5000/api/convert
			```
		- Errors are returned as JSON with an `error` key and appropriate HTTP status code.

## Developer Workflows
- **Run locally:** `python Web_app_New.py` (ensure Flask and dependencies are installed)
- **Dependencies:**
		- Python 3.x
		- Flask
		- requests
		- pymarc
		- openpyxl
	Install with:
	```bash
	pip install flask requests pymarc openpyxl
	```
- **No explicit test/build scripts** (add if project grows)
- **Debugging:** Use Flask debug mode; inspect data transformations in `Web_app_New.py`.

## Conventions & Patterns
- All logic is currently in a single file (`Web_app_New.py`).
- Output format selection is user-driven via the web UI.
- MARC parsing and KBART mapping are custom, not using external libraries for these transforms.
- No database or persistent storage; all processing is in-memory per request.

## Integration Points
- **External:** The Palace Project MARC endpoint (HTTP fetch)
- **Output:** File download (TSV, XLSX, CSV)

## Example Usage
- Start app: `python Web_app_New.py`
- Access via browser, select collection, choose output format, download result.

## Recommendations for AI Agents
- Keep all new logic in `Web_app_New.py` unless refactoring for modularity.
- Follow the pattern of user-driven format selection and in-memory processing.
- Reference the README for project intent and user workflow.
- If adding dependencies, update instructions here and in README.
