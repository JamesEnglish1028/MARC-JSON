

# MARC-Converter

MARC-Converter is a Python package and Flask web app for converting MARC records (from The Palace Project, uploaded files, or remote URLs) into KBART-style inventory files (TSV, XLSX, or CSV).


## Features
- Web UI for selecting collections and output format
- API endpoint for programmatic MARC-to-JSON conversion
- Output in KBART (TSV), Excel (.xlsx), or CSV
- Accepts MARC files via upload or remote URL
- Optional Bearer token security for API


## Project Structure
- `marc_converter/` — Main package (Flask app, logic, API, static assets)
- `setup.py`, `requirements.txt` — Packaging and dependencies
- `Procfile`, `render.yaml` — Render.com deployment config


## Quickstart (Local)
```bash
git clone <repo-url>
cd MARC-Converter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Or install as a package (recommended for development):
pip install -e .
```


## Running Locally
```bash
# Run with Flask's built-in server (development only):
python -m marc_converter
# Or with Gunicorn (recommended for production):
gunicorn -w 4 -b 0.0.0.0:10000 marc_converter.app:app
# Or use the provided script:
./run-local.sh
```
Visit [http://localhost:10000](http://localhost:10000) in your browser.


## Deploying to Render.com
1. Push this repo to your Git provider (GitHub, GitLab, etc.)
2. Create a new **Web Service** on Render, point to this repo
3. Render will use `render.yaml` and `Procfile` to build and run the app
4. The app will be available at your Render URL



## API Usage
The app exposes a programmatic API for MARC conversion, suitable for integration with other apps or automation tools.



### `POST /api/convert`
- **Endpoint:** `/api/convert`
- **Method:** `POST`
- **Authentication (optional):** If `API_TOKEN` is set, include header `Authorization: Bearer <token>`
- **Accepts:**
  - `multipart/form-data` with a `file` field (MARC file upload)
  - or `application/json` with a `url` field (remote MARC file URL)


#### Example Request: File Upload (curl)
```bash
curl -F "file=@yourfile.mrc" http://localhost:10000/api/convert
```


#### Example Request: URL Ingestion (curl)
```bash
curl -H "Content-Type: application/json" -d '{"url": "https://example.com/yourfile.mrc"}' http://localhost:10000/api/convert
```


#### Example with Token
```bash
curl -H "Authorization: Bearer <your_token>" -F "file=@yourfile.mrc" http://localhost:10000/api/convert
```


#### Request Schema
- **File:**
  - Form field `file` (MARC21 binary file)
- **URL:**
  - JSON body: `{ "url": "https://..." }`


#### Response Schema
- **Success (HTTP 200):**
  - Returns a JSON array of MARC records, each as a dictionary (see [pymarc as_dict](https://pymarc.readthedocs.io/en/latest/api/pymarc.html#pymarc.Record.as_dict)).
  - Example:
    ```json
    [
      {
        "leader": "...",
        "fields": [ ... ]
      },
      ...
    ]
    ```
- **Error (HTTP 400/500):**
  - Returns a JSON object with an `error` key and a message.
  - Example:
    ```json
    { "error": "No file uploaded" }
    ```


#### Integration Tips for Developers & AI Agents
- No authentication is required by default (add as needed via `API_TOKEN` env var).
- The endpoint is stateless; each request is independent.
- Use standard HTTP libraries to POST files (e.g., `requests` in Python, `fetch` in JS, `curl` in shell).
- Validate the response: check for HTTP 200 and parse the JSON; on error, handle the `error` key.
- The output JSON structure matches pymarc's `as_dict()`; see [pymarc docs](https://pymarc.readthedocs.io/en/latest/api/pymarc.html#pymarc.Record.as_dict) for field details.
- For large files, expect a large JSON array in the response.




#### Example Integration (Python)
```python
import requests

# File upload
with open("yourfile.mrc", "rb") as f:
    resp = requests.post(
        "http://localhost:10000/api/convert",
        files={"file": f},
        headers={"Authorization": "Bearer <your_token>"}  # optional
    )
    if resp.ok:
        records = resp.json()
        # process records
    else:
        print("Error:", resp.json()["error"])

# URL ingestion
resp = requests.post(
    "http://localhost:10000/api/convert",
    json={"url": "https://example.com/yourfile.mrc"},
    headers={"Authorization": "Bearer <your_token>"}  # optional
)
if resp.ok:
    records = resp.json()
else:
    print("Error:", resp.json()["error"])
```



#### Example Integration (React/JavaScript)
```jsx
// File upload
async function uploadMarcFile(file, token) {
  const formData = new FormData();
  formData.append('file', file);
  const resp = await fetch('http://localhost:10000/api/convert', {
    method: 'POST',
    headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    body: formData
  });
  if (resp.ok) {
    const records = await resp.json();
    return records;
  } else {
    const err = await resp.json();
    throw new Error(err.error);
  }
}

// URL ingestion
async function uploadMarcUrl(url, token) {
  const resp = await fetch('http://localhost:10000/api/convert', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    },
    body: JSON.stringify({ url })
  });
  if (resp.ok) {
    const records = await resp.json();
    return records;
  } else {
    const err = await resp.json();
    throw new Error(err.error);
  }
}

// Usage in a file input handler:
// <input type="file" onChange={e => uploadMarcFile(e.target.files[0], token)} />
// Usage for URL:
// uploadMarcUrl('https://example.com/yourfile.mrc', token)
```


## Customization
- Place static assets (e.g., logo.png) in `marc_converter/static/`
- All main logic is in `marc_converter/logic.py`


## License
MIT
