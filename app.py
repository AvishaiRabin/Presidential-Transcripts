import flask
from flask import Response, request, send_file, Flask
import json
import sqlite3
import csv
app = Flask(__name__, static_url_path='/static')
@app.route('/')
def index():
	#flask.render_template('index.html')
	format_ = request.args.get("format", None)
	president = request.args.get("president", "")
	year = request.args.get("year", "")
	month = request.args.get("month", "")
	document = request.args.get("document", "")

	connection = sqlite3.connect("mydatabase.sqlite")
	connection.row_factory = dictionary_factory
	cursor = connection.cursor()

	all_records_query = "SELECT features.Title as Title, features.Notes as Notes, \
				features.Month as Month, features.Year as Year, pres.PresidentName as President, \
				doc_category.DocumentCategory as DocType, people.People as People, topics.Topic as Topic \
				FROM features, features_to_people, people, features_to_topics, topics, pres, doc_category \
				where features.PresidentID = pres.ID AND features.ID = features_to_people.FeatureID \
				AND features_to_people.PeopleID = people.ID AND features.ID = features_to_topics.FeatureID \
				AND features_to_topics.TopicID = topics.ID AND features.DocumentCategoryID = doc_category.ID %s %s;"
	appended_clause = ""
	conditions_tuple = []
	if len(president) != 0:
		appended_clause += "AND pres.PresidentName = ?"
		conditions_tuple.append(president)
	if len(year) != 0:
		appended_clause += "AND features.Year = ?"
		conditions_tuple.append(year)
	if len(month) != 0:
		appended_clause += "AND features.Month = ?"
		conditions_tuple.append(month)
	if len(document) != 0:
		appended_clause += "AND doc_category.DocumentCategory = ?"
		conditions_tuple.append(document)
	if format_ == "csv":
		cursor.execute(all_records_query % (appended_clause, ""), tuple(conditions_tuple))
		records = cursor.fetchall()
		connection.close()
		return download_csv(records, "presidential_document.csv")
	else:
		cursor.execute(all_records_query % (appended_clause, "LIMIT 10"), tuple(conditions_tuple))
		records = cursor.fetchall()
		connection.close()
		return flask.render_template('index.html', records=records)

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
