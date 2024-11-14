"""
Modul, welches die URL-Pfade für die Flask-App definiert und die
entsprechenden Inhalte anzeigt.
"""

# Imports
from flask import Blueprint, render_template, request, abort
from flask_weasyprint import HTML, CSS, render_pdf

from app import aktive

# Constants
VERSION = "0.1"
AKTIVE_HTML = 'templates/documents/aktive_template.html'
AKTIVE_CSS = 'templates/documents/aktive_template.css'

# Routes
pages = Blueprint('pages',__name__,
                  template_folder='templates',
                  static_folder='static')

@pages.route('/index')
@pages.route('/')
def index():
    """
    Zeigt das Formular zur Erstellung einer Aktivenabrechnung an
    """
    return render_template('form_aktive.html', version=VERSION)

@pages.route('/Aktivenabrechnung.pdf', methods=['GET'])
def aktive_pdf():
    """
    Zeigt eine Aktivenabrechnung als PDF-Datei an.

    Daten werden aus einem GET-Querystring ausgelesen. Falls es keinen
    gibt, wird ein vorgefertigtes leeres PDF-Dokument angezeigt.
    """
    if request.method == 'GET' and request.args:
        # Query provided; create new PDF
        abrechnung = aktive.Abrechnung()
        try:
            # Get data from query string
            abrechnung.evaluate_query(request.args.to_dict())
        except:
            # Bad Request
            abort(400)
        # Prepare document as HTML
        printer = aktive.HTMLPrinter(AKTIVE_HTML)
        document = printer.html_compose(abrechnung)
        # Read in CSS file
        with open(AKTIVE_CSS) as f:
            formatting = f.read()
        # Create PDF from HTML and CSS
        return render_pdf(HTML(string=document),
                          stylesheets=[CSS(string=formatting)])
    else:
        # No query provided; use premade empty PDF instead
        return pages.send_static_file('blank/aktive.pdf')

@pages.route('/favicon.ico')
def favicon():
    """Returns the favicon."""
    return pages.send_static_file('img/favicon.ico')