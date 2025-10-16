# CLI harness for direct MARC file processing with error logging
if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) < 2:
        print("Usage: python -m marc_converter.logic <file.mrc>")
        sys.exit(1)
    marc_path = sys.argv[1]
    errors = []
    records = []
    try:
        with open(marc_path, "rb") as fh:
            reader = MARCReader(fh, to_unicode=True, force_utf8=True, utf8_handling="ignore")
            for idx, rec in enumerate(reader):
                try:
                    row = marc_to_row(rec)
                    records.append(row)
                except Exception as rec_err:
                    errors.append(f"Record {idx+1}: {rec_err}")
        print(json.dumps(records, indent=2, ensure_ascii=False))
        if errors:
            print("\nErrors encountered during parsing:")
            for err in errors:
                print(err)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# CLI harness for direct MARC file processing with error logging
if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) < 2:
        print("Usage: python -m marc_converter.logic <file.mrc>")
        sys.exit(1)
    marc_path = sys.argv[1]
    errors = []
    records = []
    try:
        with open(marc_path, "rb") as fh:
            reader = MARCReader(fh, to_unicode=True, force_utf8=True, utf8_handling="ignore")
            for idx, rec in enumerate(reader):
                try:
                    row = marc_to_row(rec)
                    records.append(row)
                except Exception as rec_err:
                    errors.append(f"Record {idx+1}: {rec_err}")
        print(json.dumps(records, indent=2, ensure_ascii=False))
        if errors:
            print("\nErrors encountered during parsing:")
            for err in errors:
                print(err)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
# Core logic for MARC processing and file generation
import tempfile
import os
import requests
from flask import send_file, jsonify
from pymarc import MARCReader, PymarcException
from openpyxl import Workbook
import csv
import unicodedata
import re

def process_marc_url(marc_url, fmt):
    if not marc_url.startswith('http'):
        return "<h3>Invalid URL format. Please provide a valid URL for the MARC file.</h3>"
    try:
        r = requests.get(marc_url)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"<h3>Error fetching MARC file: {e}</h3>"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mrc") as f:
            f.write(r.content)
            temp_path = f.name
        with open(temp_path, 'rb') as fh:
            reader = MARCReader(fh)
            data = [marc_to_row(rec) for rec in reader]
    except PymarcException as e:
        return f"<h3>Error processing MARC file: {e}</h3>"
    except Exception as e:
        return f"<h3>An unexpected error occurred: {e}</h3>"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    try:
        output_path = generate_output_file(data, fmt)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"<h3>Error generating output file: {e}</h3>"


def process_marc_file_upload(file, fmt='json'):
    try:
        reader = MARCReader(file)
        if fmt == 'json':
            records = [marc_to_row(rec) for rec in reader]
            return jsonify(records)
        elif fmt in ('csv', 'tsv'):
            records = [marc_to_row(rec) for rec in reader]
            delimiter = '\t' if fmt == 'tsv' else ','
            import io
            output = io.StringIO()
            headers = list(records[0].keys()) if records else []
            writer = csv.DictWriter(output, fieldnames=headers, delimiter=delimiter)
            writer.writeheader()
            for row in records:
                writer.writerow(row)
            output.seek(0)
            from flask import Response
            mimetype = 'text/tab-separated-values' if fmt == 'tsv' else 'text/csv'
            return Response(output.read(), mimetype=mimetype,
                            headers={"Content-Disposition": f"attachment;filename=output.{fmt}"})
        else:
            return jsonify({'error': f'Unsupported format: {fmt}'}), 400
    except PymarcException as e:
        return jsonify({'error': f'Error processing MARC file: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

def process_marc_url_api(marc_url, fmt='json'):
    if not marc_url.startswith('http'):
        return jsonify({'error': 'Invalid URL format'}), 400
    try:
        r = requests.get(marc_url)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error fetching MARC file: {e}'}), 400
    try:
        import io
        reader = MARCReader(io.BytesIO(r.content))
        if fmt == 'json':
            records = [marc_to_row(rec) for rec in reader]
            return jsonify(records)
        elif fmt in ('csv', 'tsv'):
            records = [marc_to_row(rec) for rec in reader]
            delimiter = '\t' if fmt == 'tsv' else ','
            output = io.StringIO()
            headers = list(records[0].keys()) if records else []
            writer = csv.DictWriter(output, fieldnames=headers, delimiter=delimiter)
            writer.writeheader()
            for row in records:
                writer.writerow(row)
            output.seek(0)
            from flask import Response
            mimetype = 'text/tab-separated-values' if fmt == 'tsv' else 'text/csv'
            return Response(output.read(), mimetype=mimetype,
                            headers={"Content-Disposition": f"attachment;filename=output.{fmt}"})
        else:
            return jsonify({'error': f'Unsupported format: {fmt}'}), 400
    except PymarcException as e:
        return jsonify({'error': f'Error processing MARC file: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

# --- MARC/KBART utility functions --- #
def get_subfield(field, code):
    return field.get_subfields(code)[0] if field and field.get_subfields(code) else None

def clean_unicode(text):
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.strip()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = ''.join(ch for ch in text if ch.isprintable())
    return text

def get_publication_type(record):
    bib_level = record.leader[7]
    if bib_level == 's':
        return "serial"
    elif bib_level == 'm':
        return "monograph"
    else:
        return "other"

def get_access_type(record):
    for field in record.get_fields('506'):
        restriction_note = " ".join(field.get_subfields('a')).lower()
        if any(term in restriction_note for term in ['unrestricted', 'open', 'no restrictions']):
            return "openaccess"
    for field in record.get_fields('856'):
        if field.indicator2 == '0':
            return "openaccess"
        if 'z' in field and 'subscription' in " ".join(field.get_subfields('z')).lower():
            return "paid"
    return "paid"

def get_pub_info(record):
    publisher_name = date_monograph_published_online = ""
    for field in record.get_fields('264'):
        if field.indicator2 == '1':
            publisher_name = get_subfield(field, 'b') or ""
            date_monograph_published_online = get_subfield(field, 'c') or ""
            return publisher_name.strip(), date_monograph_published_online.strip()
    fields_260 = record.get_fields('260')
    if fields_260:
        publisher_name = get_subfield(fields_260[0], 'b') or ""
        date_monograph_published_online = get_subfield(fields_260[0], 'c') or ""
    return publisher_name.strip(), date_monograph_published_online.strip()

def marc_to_row(record):
    title_id = clean_unicode(record['001'].value()) if '001' in record else "unknown"
    publication_title = clean_unicode(f"{get_subfield(record['245'], 'a') or ''} {get_subfield(record['245'], 'b') or ''}".strip())
    first_author = ""
    for tag in ('100', '110', '111'):
        for field in record.get_fields(tag):
            name = get_subfield(field, 'a')
            if name:
                first_author = clean_unicode(name)
                break
        if first_author:
            break
    first_editor = next(
        (clean_unicode(get_subfield(f, 'a')) for f in record.get_fields('700') if 'e' in f and 'editor' in " ".join(f.get_subfields('e')).lower()),
        ""
    )
    online_identifier_list = [
        clean_unicode(get_subfield(f, 'a'))
        for f in record.get_fields('020') if get_subfield(f, 'a')
    ]
    online_identifier = "; ".join(online_identifier_list)
    publisher_name, date_monograph_published_online = get_pub_info(record)
    publisher_name = clean_unicode(publisher_name)
    date_monograph_published_online = clean_unicode(date_monograph_published_online)
    title_url = "N/A"
    for field in record.get_fields('856'):
        url = get_subfield(field, 'u')
        if url:
            title_url = clean_unicode(url)
            break
    publication_type = get_publication_type(record)
    access_type = get_access_type(record)

    # --- Source ID and Type logic (refined DOI recognition) ---
    source_id = ""
    source_id_type = ""
    doi_regex = re.compile(r"(?:10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE)
    doi_url_regex = re.compile(r"https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE)

    # 1. Doc ID (ProQuest)
    if title_id.startswith("urn:librarysimplified.org/terms/id/ProQuest%20Doc%20ID/"):
        source_id = title_id.split("/ProQuest%20Doc%20ID/")[-1]
        source_id_type = "Doc ID"
    # 2. File Handle (OAPEN)
    elif title_id.startswith("https://library.oapen.org/handle/"):
        source_id = title_id.split("/handle/")[-1]
        source_id_type = "File Handle"
    # 3. Media ID (Open Research Library)
    elif title_id.startswith("urn:uuid:"):
        source_id = title_id
        source_id_type = "Media ID"
    # 4. DOI (URL form in title_id or title_url)
    elif title_id.startswith("https://doi.org/") or title_id.startswith("https://dx.doi.org/"):
        source_id = title_id
        source_id_type = "DOI"
    elif title_url.startswith("https://doi.org/") or title_url.startswith("https://dx.doi.org/"):
        source_id = title_url
        source_id_type = "DOI"
    # 5. DOI (bare string in title_id, online_identifier, or title_url)
    elif doi_regex.match(title_id):
        source_id = doi_regex.match(title_id).group(0)
        source_id_type = "DOI"
    elif any(doi_regex.match(oid) for oid in online_identifier_list):
        source_id = next(oid for oid in online_identifier_list if doi_regex.match(oid))
        source_id_type = "DOI"
    elif doi_regex.match(title_url):
        source_id = doi_regex.match(title_url).group(0)
        source_id_type = "DOI"
    # 6. ISBN
    elif online_identifier_list:
        source_id = online_identifier_list[0]
        source_id_type = "ISBN"
    else:
        source_id = title_id
        source_id_type = "Unknown"

    return {
        "title_id": title_id,
        "publication_title": publication_title,
        "title_url": title_url,
        "first_author": first_author,
        "online_identifier": online_identifier,
        "publisher_name": publisher_name,
        "publication_type": publication_type,
        "date_monograph_published_online": date_monograph_published_online,
        "first_editor": first_editor,
        "access_type": access_type,
        "source_id": source_id,
        "source_id_type": source_id_type
    }

def generate_output_file(records, fmt):
    headers = [
        "publication_title",
        "print_identifier",
        "online_identifier",
        "date_first_issue_online",
        "num_first_vol_online",
        "num_first_issue_online",
        "date_last_issue_online",
        "num_last_vol_online",
        "num_last_issue_online",
        "title_url",
        "first_author",
        "title_id",
        "embargo_info",
        "coverage_depth",
        "notes",
        "publisher_name",
        "publication_type",
        "date_monograph_published_print",
        "date_monograph_published_online",
        "monograph_volume",
        "monograph_edition",
        "first_editor",
        "parent_publication_title_id",
        "preceding_publication_title_id",
        "access_type",
        "source_id",
        "source_id_type"
    ]
    delimiter = "\t" if fmt == "tsv" else ","
    with open(f"output.{fmt}", "w", encoding="utf-8") as f:
        f.write(delimiter.join(headers) + "\n")
        for record in records:
            row = [
                record.get("publication_title", ""),
                record.get("print_identifier", ""),
                record.get("online_identifier", ""),
                record.get("date_first_issue_online", ""),
                record.get("num_first_vol_online", ""),
                record.get("num_first_issue_online", ""),
                record.get("date_last_issue_online", ""),
                record.get("num_last_vol_online", ""),
                record.get("num_last_issue_online", ""),
                record.get("title_url", ""),
                record.get("first_author", ""),
                record.get("title_id", ""),
                record.get("embargo_info", ""),
                record.get("coverage_depth", "fulltext"),
                record.get("notes", ""),
                record.get("publisher_name", ""),
                record.get("publication_type", "monograph"),
                record.get("date_monograph_published_print", ""),
                record.get("date_monograph_published_online", ""),
                record.get("monograph_volume", ""),
                record.get("monograph_edition", ""),
                record.get("first_editor", ""),
                record.get("parent_publication_title_id", ""),
                record.get("preceding_publication_title_id", ""),
                record.get("access_type", "paid"),
                record.get("source_id", ""),
                record.get("source_id_type", "")
            ]
            f.write(delimiter.join(row) + "\n")
