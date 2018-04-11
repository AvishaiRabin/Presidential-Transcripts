import flask
from flask import Response, request, send_file, Flask
import json
import sqlite3
import csv
app = Flask(__name__, static_url_path='/static')
@app.route('/')
def index():

	return flask.render_template('index.html')
if __name__ == '__main__':
    app.debug=True
    app.run()
