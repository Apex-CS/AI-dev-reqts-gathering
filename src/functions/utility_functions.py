import streamlit as st
import re

import src.components.streamlit_elements as st_elems

# --- Sidebar ---
allowed_types = ["txt", "pdf", "docx", "doc", "md", "rtf"]
allowed_mime_types = [
    "text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword", "application/txt", "application/md", "application/rtf"
]

# --- Constants ---
SETTINGS_DB = "planningverse/settings.db"
DOCS_DB = "planningverse/documents.db"
REFS_DB = "planningverse/reference_links.db"

def is_url(text):
    url_regex = re.compile(r'^(https?://|www\.)[^\s]+$', re.IGNORECASE)
    return bool(url_regex.match(text))

def clean_html(text):
    if not text:
        return ""
    text = re.sub('<[^<]+?>', '', text)
    return text.replace("</br>", "\n").replace("</li>", "\n")

def get_field(fields, key, default=""):
    value = fields.get(key, default)
    return value.get('displayName', default) if isinstance(value, dict) else value


def extract_json_blocks(text):
    pattern = r'```json\s*([\s\S]*?)\s*```'
    json_blocks = []
    for match in re.findall(pattern, text, re.DOTALL):
        try:
            json_blocks.append(json.loads(match))
        except Exception:
            continue
    return json_blocks