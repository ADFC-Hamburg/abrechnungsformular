#!/usr/bin/env python3

from flask import Flask, render_template

from app import aktive

server = Flask(__name__)

@server.route('/index')
@server.route('/')
def index():
    return render_template('form_aktive.html')

if __name__ == '__main__':
    server.run(host='0.0.0.0',port=5000)
