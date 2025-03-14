import json


class PATHS():
    PDF_TEMPLATE_FOLDER = 'templates/documents/'
    AKTIVE_HTML = 'aktive_template.html'
    AKTIVE_CSS = 'aktive_template.css'


def _fetch_json(path:str):
    with open(path) as f:
        data = json.load(f)
        return data

def _fetch_version(path:str) -> str:
    with open(path) as f:
        version = f.readline()
    return version

#: Die Versionsnummer dieser App.
VERSION = _fetch_version('VERSION')
#: Die Kontaktdaten des Vereins.
CONTACT = _fetch_json('CONTACT.json')
