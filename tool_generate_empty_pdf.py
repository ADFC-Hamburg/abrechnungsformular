#!/usr/bin/env python3

"""
Dieses Script erstellt eine leere Version des Aktivenabrechnungsfomulars
und speichert diese unter static/blank/Aktivenabrechnung.pdf
"""

from weasyprint import HTML

from app import aktive, PATHS

WRITEPATH = "static/blank/Aktivenabrechnung.pdf"

aktivenabrechnung = HTML(string=aktive.Abrechnung().html_compose(),
                         base_url=PATHS.PDF_TEMPLATE_FOLDER)
aktivenabrechnung.write_pdf(WRITEPATH)