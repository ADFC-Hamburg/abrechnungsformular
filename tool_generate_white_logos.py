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

DESCRIPTION = "Dieses Script erstellt weiße Varianten transparenter SVG-Dateien" \
+" und speichert diese im gleichen Ordner."

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('file',nargs='+',help='Die zu bearbeitende(n) SVG-Datei(en)')
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
args=parser.parse_args()


from pathlib import Path
from re import sub

def semiwhite(svg:str):
    return sub("#[0-7][0-9a-fA-F][0-7][0-9a-fA-F]{3}","#ffffff",svg)

def white(svg:str):
    return sub("#[0-9a-fA-F]{6}","#ffffff",svg)

for file in args.file:
    path = Path(file)
    with path.open() as f:
        svg = f.read()
        svg_semi = semiwhite(svg)
        svg_white = white(svg_semi)
        path_semi = path.with_stem(path.stem+'-semiwhite')
        path_white = path.with_stem(path.stem+'-white')
        if not path_semi.exists():
            path_semi.write_text(svg_semi)
        if not path_white.exists():
            path_white.write_text(svg_white)