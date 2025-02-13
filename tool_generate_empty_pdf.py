#!/usr/bin/env python3

"""
Dieses Script erstellt eine leere Version des Aktivenabrechnungsfomulars
und speichert diese unter static/blank/Aktivenabrechnung.pdf
"""

from weasyprint import HTML,CSS

HTMLPATH = "templates/documents/aktive_template.html"
CSSPATH = "templates/documents/aktive_template.css"
WRITEPATH = "static/blank/Aktivenabrechnung.pdf"
REMOVETEXT = "(Bei digitaler Einreichung nicht notwendig.)"

string = ""
for i in range(1,8):
    string += "\t"*4+"<tr><td>"+str(i)+"</td>"+"<td></td>"*7+"</tr>\n"

with open(HTMLPATH) as f:
    content = f.read()

content = content.replace("<!--SPLIT-->\n<!--POSITIONS-->",string)
content = content.replace('<td class="check"><!--PLACEHOLDER--></td>','<td class="check">&#9744;<!--PLACEHOLDER--></td>')
content = content.replace(REMOVETEXT,"")

fin = HTML(string=content)
css = CSS(CSSPATH)
fin.write_pdf(WRITEPATH, stylesheets=[css])