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


def process_marc_file_upload(file):
    try:
        reader = MARCReader(file)
        records = [rec.as_dict() for rec in reader]
        return jsonify(records)
    except PymarcException as e:
        return jsonify({'error': f'Error processing MARC file: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

def process_marc_url_api(marc_url):
    if not marc_url.startswith('http'):
        return jsonify({'error': 'Invalid URL format'}), 400
    try:
        r = requests.get(marc_url)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error fetching MARC file: {e}'}), 400
    try:
        reader = MARCReader(r.content)
        records = [rec.as_dict() for rec in reader]
        return jsonify(records)
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
    online_identifier = [
        clean_unicode(get_subfield(f, 'a'))
        for f in record.get_fields('020') if get_subfield(f, 'a')
    ]
    online_identifier = "; ".join(online_identifier)
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
        "access_type": access_type
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
        "access_type"
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
                record.get("access_type", "paid")
            ]
            f.write(delimiter.join(row) + "\n")
