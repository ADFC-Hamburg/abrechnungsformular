#!/usr/bin/env python3

"""
Startet einen Flask-Server, welcher eine Webseite anbietet, auf der
Benutzer ein Formular für eine Aktivenabrechnung ausfüllen und
anschließend eine fertige Abrechnung im PDF-Format herunterladen
können.
"""

# Imports
from flask import Flask

from app import routes

# App
flaskapp = Flask(__name__, static_folder=None)
flaskapp.register_blueprint(routes.pages)

# Executable
if __name__ == '__main__':
    flaskapp.run(host='0.0.0.0')
