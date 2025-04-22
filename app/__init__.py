import configparser


class PATHS():
    PDF_TEMPLATE_FOLDER = 'templates/documents/'
    AKTIVE_HTML = 'aktive_template.html'
    AKTIVE_CSS = 'aktive_template.css'
    REISE_HTML = 'reise_template.html'
    REISE_CSS = 'reise_template.css'
    CONFIG_FILE = 'CONFIG.ini'


def _fetch_version(path:str) -> str:
    with open(path) as f:
        version = f.readline()
    return version

def _fetch_config(path:str) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    with open(path) as f:
        config.read_file(f)
    return config

def _read_contacts(config:configparser.ConfigParser) -> dict[str,str]:
    KEYS = {'Name':'NameVollständig','NameShort':'NameAbgekürzt',
            'LineOne':'AdresseZeile1','LineTwo':'AdresseZeile2',
            'LineThree':'AdresseZeile3','PostCode':'Postleitzahl',
            'City':'Stadt','State':'Bundesland','Country':'Ländercode',
            'Phone':'Telefonnummer','Mail':'EMailAdresse','IBAN':'KontoIBAN',
            'AccName':'KontoName','BIC':'KontoBIC','VAT':'KontoVAT',
            'WebLegal':'WebImpressum','WebPrivacy':'WebDatenschutz'}
    out = {}
    for key in KEYS.keys():
        out[key] = config['Kontaktdaten'][KEYS[key]]\
            if config.has_option('Kontaktdaten',KEYS[key]) else ''
    return out

def _read_reise_rate(config:configparser.ConfigParser) -> dict[str,str]:
    KEYS1 = {'GanzerTag':'TagessatzGanz','AnAbreise':'TagessatzReduziert',
             'Einzeltag':'TagessatzEinzeltag'}
    KEYS2 = {'PKWproKM':'FahrtgeldProKM','PKWMaximum':'FahrtgeldMaximum',
             'UebernachtMin':'Übernachtungspauschale'}
    out = {'Tagessatz':{}}
    for key in KEYS1.keys():
        out['Tagessatz'][key] = config['Reisepauschalen'][KEYS1[key]]\
            if config.has_option('Reisepauschalen',KEYS1[key]) else ''
    for key in KEYS2.keys():
        out[key] = config['Reisepauschalen'][KEYS2[key]]\
            if config.has_option('Reisepauschalen',KEYS2[key]) else ''
    return out


#: Die Versionsnummer dieser App.
VERSION = _fetch_version('VERSION')

config = _fetch_config(PATHS.CONFIG_FILE)
#: Die Kontaktdaten des Vereins.
CONTACT = _read_contacts(config)
#: Die Geldsätze für Reisekostenabrechnungen.
REISE_RATE = _read_reise_rate(config)