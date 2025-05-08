#!/usr/bin/env python3

"""
Dieses Script erstellt weiße Versionen des Firmenlogos.
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

DESCRIPTION = "Dieses Script erstellt weiße Varianten transparenter" \
+" SVG-Dateien und speichert diese im gleichen Ordner." \
+" Vorhandene Dateien werden dabei nicht überschrieben."

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('file',nargs='+',help='Die zu bearbeitende(n) SVG-Datei(en)')
parser.add_argument('-o','--overwrite',action='store_true',help='Überschreibe existierende Dateien')
parser.add_argument('-v','--verbose',action='store_true',help='Gib ausführlichere Logs aus')
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
args=parser.parse_args()


from pathlib import Path
from re import sub

def semiwhite(svg:str) -> str:
    return sub("#[0-7][0-9a-fA-F][0-7][0-9a-fA-F]{3}","#ffffff",svg)

def white(svg:str) -> str:
    return sub("#[0-9a-fA-F]{6}","#ffffff",svg)

def create_file(path:Path,svg:str):
    if not path.exists() or args.overwrite:
        path.write_text(svg)
        if args.verbose:
            print(f'Erstellt: {str(path)}')
    elif args.verbose:
        print(f'Die Datei {str(path)} existiert bereits.')

for file in args.file:
    path = Path(file)
    try:
        f = path.open()
    except FileNotFoundError:
        print(f"'Die Datei '{file}' existiert nicht.")
        exit(2)
    else:
        with f:
            svg = f.read()
            svg_semi = semiwhite(svg)
            svg_white = white(svg_semi)
            path_semi = path.with_stem(path.stem+'-semiwhite')
            path_white = path.with_stem(path.stem+'-white')
            create_file(path_semi,svg_semi)
            create_file(path_white,svg_white)