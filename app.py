import flask
from flask import Response, request, send_file, Flask
import json
import sqlite3
import csv
app = Flask(__name__, static_url_path='/static')
@app.route('/')
def index():
	return flask.render_template('index.html')

@app.route('/president')
def president():
	format_ = request.args.get("format", None)
	president = request.args.get("president", "")
	year = request.args.get("year", "")
	month = request.args.get("month", "")
	document = request.args.get("document", "")

	connection = sqlite3.connect("mydatabase.sqlite")
	connection.row_factory = dictionary_factory
	cursor = connection.cursor()


if __name__ == '__main__':
    app.debug=True
    app.run()
