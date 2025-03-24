"""
Modul, welches die URL-Pfade für die Flask-App definiert und die
entsprechenden Inhalte anzeigt.
"""

# Imports
from io import BytesIO

from drafthorse.pdf import attach_xml
from flask import Blueprint, render_template, request, abort, send_file
from weasyprint import HTML

from . import aktive, reise, PATHS, CONTACT, REISE_RATE, VERSION

# Constants
STATIC = 'pages.static'

# Routes
pages = Blueprint('pages',__name__,
                  template_folder='templates',
                  static_folder='../static',
                  static_url_path='/static')

@pages.route('/index')
@pages.route('/')
def index():
    """
    Zeigt das Formular zur Erstellung einer Aktivenabrechnung an
    """
    return render_template('form_aktive.html', static=STATIC, version=VERSION,
                           address=CONTACT)

@pages.route('/reisekosten')
def reise_form():
    """
    Zeigt das Formular zur Erstellung einer Reisekostenabrechnung an
    """
    return render_template('form_reise.html', static=STATIC, version=VERSION,
                           address=CONTACT, rates=REISE_RATE,
                           abrechnung=reise.Abrechnung)

@pages.route('/abrechnung', methods=['GET'])
def aktive_pdf():
    """
    Zeigt eine Aktivenabrechnung als PDF-Datei an.

    Daten werden aus einem GET-Querystring ausgelesen. Falls es keinen
    gibt, wird ein vorgefertigtes leeres PDF-Dokument angezeigt.
    """
    if request.method == 'GET' and request.args:
        # Query provided; create new PDF
        abrechnung = aktive.Abrechnung()
        # Get data from query string
        errormessage = abrechnung.evaluate_query(request.args.to_dict())
        if errormessage:
            abort(400, errormessage)
        # Prepare electronic invoice as XML
        xml = abrechnung.factur_x()
        # Prepare document as HTML
        document = abrechnung.html_compose()
        # Select a filename for the resulting file
        filename = abrechnung.suggest_filename()+'.pdf'
        # Create PDF from HTML document
        html = HTML(string=document,base_url=PATHS.PDF_TEMPLATE_FOLDER)
        pdf = html.write_pdf()
        # Attach electronic invoice
        pdf = attach_xml(pdf, xml)
        # Return file
        return send_file(BytesIO(pdf), mimetype='application/pdf',
                         as_attachment=True, download_name=filename)
    else:
        # No query provided; use premade empty PDF instead
        return pages.send_static_file('blank/Aktivenabrechnung.pdf')

@pages.route('/reisekosten/abrechnung', methods=['GET'])
def reise_pdf():
    """WIP"""
    if request.method == 'GET' and request.args:
        abrechnung = reise.Abrechnung()
        errormessage = abrechnung.evaluate_query(request.args.to_dict())
        if errormessage:
            abort(400, errormessage)
        return str(abrechnung.gettotal())
    else:
        # No query provided
        abort(400)

@pages.route('/favicon.ico')
def favicon():
    """Returns the favicon."""
    return pages.send_static_file('img/favicon.ico')
