from flask import Response, request, send_file, Flask
import json
import sqlite3
import csv
app = Flask(_name_)
@app.route('/')
def index():
	"""
	Displays the home page that leads users into different pages
	"""
	return flask.render_template('index.html')
