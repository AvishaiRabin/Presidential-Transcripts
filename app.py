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

	all_records_query = "SELECT f.Title as Title, f.Notes as Notes, \
				f.Month as Month, f.Year as Year, p.PresidentName as President, \
				dc.DocumentCategory as DocType, pe.People as People, t.Topic as Topic \
				FROM features f INNER JOIN pres p ON f.PresidentID = p.ID LEFT JOIN features_to_people ftp ON \
				f.ID = ftp.FeatureID LEFT JOIN people pe ON ftp.PeopleID = pe.ID LEFT JOIN features_to_topics ftt ON \
				f.ID = ftt.FeatureID LEFT JOIN topics t ON ftt.TopicID = t.ID LEFT JOIN doc_category dc ON \
				f.DocumentCategoryId = dc.ID %s %s;"
	"""	features_to_people, people, features_to_topics, topics, pres, doc_category \
	where features.PresidentID = pres.ID AND features.ID = features_to_people.FeatureID \
	AND features_to_people.PeopleID = people.ID AND features.ID = features_to_topics.FeatureID \
	AND features_to_topics.TopicID = topics.ID AND features.DocumentCategoryID = doc_category.ID %s %s;"""
	appended_clause = "WHERE "
	appended = False
	conditions_tuple = []
	if len(president) != 0:
		appended_clause += "p.PresidentName = ?"
		conditions_tuple.append(president)
		appended = True
	if len(year) != 0:
		if not appended:
			appended_clause += "f.Year = ?"
		else:
			appended_clause += "AND f.Year = ?"
		conditions_tuple.append(year)
		appended = True
	if len(month) != 0:
		if not appended:
			appended_clause += "f.Month = ?"
		else:
			appended_clause += "AND f.Month = ?"
		conditions_tuple.append(month)
		appended = True
	if len(document) != 0:
		if not appended:
			appended_clause += "dc.DocumentCategory = ?"
		else:
			appended_clause += "AND dc.DocumentCategory = ?"
		conditions_tuple.append(document)
		appended = True
	if not appended:
		appended_clause = ""
	if format_ == "csv":
		cursor.execute(all_records_query % (appended_clause, ""), tuple(conditions_tuple))
		records = cursor.fetchall()
		connection.close()
		return download_csv(records, "presidential_document.csv")
	else:
		cursor.execute(all_records_query % (appended_clause, "LIMIT 20"), tuple(conditions_tuple))
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
