import flask
from flask import Response, request, send_file, Flask
import json
import sqlite3
import csv
app = Flask(__name__, static_url_path='/static')
@app.route('/')
def index():
	return flask.render_template('index.html')

@app.route('/')
def president():
	format_ = request.args.get("format", None)
	#president = request.args.get("president", "")
	year = request.args.get("year", "")
#	month = request.args.get("month", "")
#	document = request.args.get("document", "")

	connection = sqlite3.connect("mydatabase.sqlite")
	connection.row_factory = dictionary_factory
	cursor = connection.cursor()

	all_records_query = "SELECT features.ID as ID, features.Title as Title, features.Notes as Notes, \
				features.month as month FROM features %s %s;"

	if year == "All Years":
		where_clause = ""
	else:
		where_clause = "where features.Year = ?"
	limit_statement = "limit 20" if format_ != "csv" else ""
	all_records_query = all_records_query % (where_clause, limit_statement)
	cursor.execute(all_records_query ,("%"+ year,))
	records = cursor.fetchall()
	connection.close()

	if format_ == "csv":
		return download_csv(records, "features_%s.csv" % (year))
	else:
		selected_year = int(year)
		return flask.render_template('index.html', records=records, selected_year=selected_year)

def dictionary_factory(cursor, row):
	"""
	This function converts what we get back from the database to a dictionary
	"""
	d = {}
	for index, col in enumerate(cursor.description):
		d[col[0]] = row[index]
	return d

def download_csv(data, filename):
	"""
	Pass into this function, the data dictionary and the name of the file and it will create the csv file and send it to the view
	"""
	header = data[0].keys() #Data must have at least one record.
	with open('downloads/' + filename, "w+") as f:
		writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)
		for row in data:
			writer.writerow(list(row.values()))

		#Push the file to the view
	return send_file('downloads/' + filename,
				 mimetype='text/csv',
				 attachment_filename=filename,
				 as_attachment=True)


if __name__ == '__main__':
    app.debug=True
    app.run()
