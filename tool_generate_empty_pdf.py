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

WRITEFOLDER = ""
DESCRIPTION = "Dieses Script erstellt leere Versionen der Abrechnungsformulare" \
+" und speichert diese als PDF-Dateien."
EPILOG = "WICHTIG:  Die Schriftarten Arimo und DejaVu Sans müssen installiert sein!"

parser = argparse.ArgumentParser(description=DESCRIPTION,epilog=EPILOG)
parser.add_argument('-a','--aktive',action='store_true',help='Erstellt eine leere Aktivenabrechnung')
parser.add_argument('-r','--reise',action='store_true',help='Erstellt eine leere Reisekostenabrechnung')
parser.add_argument('Pfad',nargs='?',help='Der Ordner, in dem die Formulare gespeichert werden',default=WRITEFOLDER)
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
args=parser.parse_args()


from weasyprint import HTML

from app import aktive, reise

def print_pdf(object,name:str) -> None:
    abrechnung = HTML(string=object.html_compose(),
                      base_url=PATHS.PDF_TEMPLATE_FOLDER)
    path = args.Pfad+name+'.pdf'
    abrechnung.write_pdf(path)
    print (f'Leere {name} gespeichert unter {path}')

if args.aktive:
    print_pdf(aktive.Abrechnung(),'Aktivenabrechnung')
if args.reise:
    print_pdf(reise.Abrechnung(),'Reisekostenabrechnung')