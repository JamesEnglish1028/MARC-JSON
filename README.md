

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
  - Returns a JSON array of KBART-style metadata records (when `?format=json`), or a file (CSV/TSV) if requested.
  - Example (JSON):
    ```json
    [
      {
        "title_id": "string",
        "publication_title": "string",
        "title_url": "string",
        "first_author": "string",
        "online_identifier": "string",
        "publisher_name": "string",
        "publication_type": "string",
        "date_monograph_published_online": "string",
        "first_editor": "string",
        "access_type": "string",
        "source_id": "string",
        "source_id_type": "string"
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

##### JSON Response Properties (KBART-style)

| Property                        | Type   | Description                                                      |
|----------------------------------|--------|------------------------------------------------------------------|
| `title_id`                      | string | Unique record identifier (from MARC 001)                         |
| `publication_title`             | string | Title of the publication (from MARC 245)                         |
| `title_url`                     | string | URL to the title (from MARC 856$u, if present)                   |
| `first_author`                  | string | First author (from MARC 100/110/111)                             |
| `online_identifier`             | string | Online identifier(s), e.g. ISBN(s) (from MARC 020$a)             |
| `publisher_name`                | string | Publisher name (from MARC 264/260)                               |
| `publication_type`              | string | Publication type: "monograph", "serial", or "other"             |
| `date_monograph_published_online`| string | Online publication date (from MARC 264/260)                      |
| `first_editor`                  | string | First editor (from MARC 700$e=editor)                            |
| `access_type`                   | string | "openaccess" or "paid" (from MARC 506/856)                      |
| `source_id`                     | string | Source identifier, pattern-matched from title_id, URL, ISBN, or DOI. DOI recognition supports both the alphanumeric string (e.g., `10.1000/182`) and the URL form (e.g., `https://doi.org/10.1000/182` or `https://dx.doi.org/10.1000/182`). |
| `source_id_type`                | string | Type of source ID: "DOI" (if a valid DOI string or URL is detected, including any `title_id` or `title_url` that starts with `https://doi.org/`), "ISBN", "Doc ID", "Media ID", "File Handle", or "Unknown". DOI detection uses standard DOI patterns and direct URL matching, and is not case-sensitive. |

All properties are returned as strings. If a value is missing in the MARC record, the property will be an empty string or a default value.


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


else:

    print("Error:", resp.json()["error"])
```



#### Example Integration (React/JavaScript)
```jsx

// File upload

  formData.append('file', file);
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
