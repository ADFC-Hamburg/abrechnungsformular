import json

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