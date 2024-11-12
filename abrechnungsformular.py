#!/usr/bin/env python3

"""
Startet einen Flask-Server, welcher eine Webseite anbietet, auf der
Benutzer ein Formular für eine Aktivenabrechnung ausfüllen und
anschließend eine fertige Abrechnung im PDF-Format herunterladen
können.
"""

from flask import Flask, render_template, request, abort

from app import aktive

server = Flask(__name__)

@server.route('/index')
@server.route('/')
def index():
    """
    Zeigt das Formular zur Erstellung einer Aktivenabrechnung an
    """
    return render_template('form_aktive.html')

if __name__ == '__main__':
    server.run(host='0.0.0.0',port=5000)
