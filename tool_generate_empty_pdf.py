#!/usr/bin/env python3

"""
Dieses Script erstellt leere Abrechnungsformulare.
"""


import gettext

def Übersetzung(Text):
    Text = Text.replace("usage", "Anwendung")
    Text = Text.replace("show this help message and exit",
                        "Zeige nur diese Hilfe an")
    Text = Text.replace("error:", "Fehler:")
    Text = Text.replace("the following arguments are required:",
                        "Die folgenden Argumente müssen angegeben werden:")
    return Text
gettext.gettext = Übersetzung


import argparse, sys

from app import PATHS

WRITEFOLDER = "static/blank/"
DESCRIPTION = "Dieses Script erstellt leere Versionen der Abrechnungsformulare" \
+" und speichert diese unter "+WRITEFOLDER
EPILOG = "WICHTIG:  Die Schriftarten Arimo und DejaVu Sans müssen installiert sein!"

parser = argparse.ArgumentParser(description=DESCRIPTION,epilog=EPILOG)
parser.add_argument('-a','--aktive',action='store_true',help='Erstellt eine leere Aktivenabrechnung')
parser.add_argument('-r','--reise',action='store_true',help='Erstellt eine leere Reisekostenabrechnung')
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
args=parser.parse_args()


from weasyprint import HTML

from app import aktive, reise

def print(object,name:str) -> None:
    abrechnung = HTML(string=object.html_compose(),
                      base_url=PATHS.PDF_TEMPLATE_FOLDER)
    abrechnung.write_pdf(WRITEFOLDER+name+'.pdf')

if args.aktive:
    print(aktive.Abrechnung(),'Aktivenabrechnung')
if args.reise:
    print(reise.Abrechnung(),'Reisekostenabrechnung')