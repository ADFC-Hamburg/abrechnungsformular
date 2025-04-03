import json


class PATHS():
    PDF_TEMPLATE_FOLDER = 'templates/documents/'
    AKTIVE_HTML = 'aktive_template.html'
    AKTIVE_CSS = 'aktive_template.css'
    REISE_HTML = 'reise_template.html'
    REISE_CSS = 'reise_template.css'


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
#: Die Geldsätze für Reisekostenabrechnungen.
REISE_RATE = _fetch_json('REISE_PAUSCHALE.json')