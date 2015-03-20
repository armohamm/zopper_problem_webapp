#appcfg.py -A enduring-grid-600 update appengine-try-python
from flask import Flask, render_template, request, jsonify
from flask import Flask
import datetime
import flask
import csv,sys
import MySQLdb

import time
from flask.ext.cache import Cache
app = Flask(__name__)
# Check Configuring Flask-Cache section for more details
cache = Cache(app,config={'CACHE_TYPE': 'simple'})
#cache = Cache(app,config={'CACHE_TYPE': 'simple'})
details = {}
# main index
@app.route("/")
def index():
	return render_template("index.html")

def connect_it():
	db = MySQLdb.connect("us-cdbr-iron-east-02.cleardb.net","be225b633c476c","4843cd70","heroku_e5b2294f4b320d3" )
	return db



def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'ascii') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.decode('ascii','ignore')
def slice_dict(a,b):
  sliced_dict = {}
  sliced_dict['records'] = details['records'][a:b]
  sliced_dict['total'] = len(sliced_dict['records'])
  #print sliced_dict
  return sliced_dict


def read_csv_data():
  global details
  if len(details)==0:
    f = open('all_india_pin_code.csv', 'rt')
    try:
          reader = unicode_csv_reader(f)
          listt = []
          for row in reader:
              rec = {}
              rec['officename'] = row[0]
              rec['pincode'] = row[1]
              rec['officeType'] = row[2]
              rec['Deliverystatus'] = row[3]
              rec['divisionname'] = row[4]
              rec['regionname'] = row[5]
              rec['circlename'] = row[6]
              rec['Taluk'] = row[7]
              rec['Districtname'] = row[8]
              rec['statename'] = row[9]
              listt.append(rec)
          #print a[0]
          details["records"] = listt
          details["total"] = len(details["records"])
    finally:
          f.close()

@app.route("/getAllData")
def getAllData():
  #TODO get the details from db and pass to donation details.html
  return render_template("details.html")


def build_query(filter_criteria):
  sql_query='select * from all_india_pin_code_all_india_pin_code where '
  where_clause = ''
  for each in filter_criteria:
    query_params = str(filter_criteria[each]).split(',')
    where_clause = where_clause+query_params[0]
    if query_params[1]=="is":
      where_clause = where_clause +"="
      where_clause = where_clause+query_params[2]
    if query_params[1]=="begins":
      where_clause = where_clause +" like " +"'"
      where_clause = where_clause+query_params[2]
      where_clause = where_clause+"%'"
    if query_params[1]=="contains":
      where_clause = where_clause +" like " +"'%"
      where_clause = where_clause+query_params[2]
      where_clause = where_clause+"%'"
    if query_params[1]=="ends":
      where_clause = where_clause +" like " +"'%"
      where_clause = where_clause+query_params[2]+"'"  
    where_clause = where_clause+" or "
    #print where_clause[:-4],"0000000000000000"
  sql_query = sql_query+ where_clause[:-4]
  return sql_query

def run_db_query(db_query):
  db = connect_it()
  cursor = db.cursor()
  sql = db_query
  #print sql,"++++++++++"
  # Execute the SQL command
  cursor.execute(sql)
  results = cursor.fetchall()
  query_result = {}
  listt = []
  for row in results:
      rec = {}
      rec['officename'] = row[0]
      rec['pincode'] = row[1]
      rec['officeType'] = row[2]
      rec['Deliverystatus'] = row[3]
      rec['divisionname'] = row[4]
      rec['regionname'] = row[5]
      rec['circlename'] = row[6]
      rec['Taluk'] = row[7]
      rec['Districtname'] = row[8]
      rec['statename'] = row[9]
      listt.append(rec)
  #print a[0]
  query_result["records"] = listt
  query_result["total"] = len(query_result["records"])
  db.close()
  return query_result

@app.route("/searchResult",methods=["GET","POST"])
def searchResult():
  filter_details = request.args.get('field0')
  #print request.args,"----------------------++"
  if filter_details==None:
    return render_template("details.html")
  filter_criteria = {}
  for each in request.args:
    filter_criteria[each] = request.args.get(each)
  final_query = build_query(filter_criteria)
  query_result = run_db_query(final_query)
  #print filter_criteria,"pppppppppp"
  #tmp = slice_dict(0,500)
  #  print tmp,"-------------"
  #TODO get the details from db and pass to donation details.html
  return render_template("search.html", details= query_result)


@app.route("/searchAPI",methods=["GET","POST"])
def searchAPI():
  filter_details = request.args.get('field0')
  #print request.args,"----------------------++"
  filter_criteria = {}
  if filter_details==None:
    return flask.jsonify(**{'Error':"You didn't pass any filters"})
  for each in request.args:
    filter_criteria[each] = request.args.get(each)
  final_query = build_query(filter_criteria)
  query_result = run_db_query(final_query)
  print query_result,"************"
  return flask.jsonify(**query_result)


@app.route("/readFromExcel", methods=["GET","POST"])
def readFromExcel():
  return render_template("readFromExcel.html")

  
@app.route("/resultSet", methods=["GET","POST"])
def resultSet():
  import json
  ran_a = int(request.args.get('range_a'))
  ran_b = int(request.args.get('range_b'))
  read_csv_data()
  if ran_b==-1:
      return flask.jsonify(**details)
  #print details[ran_a:ran_b]
    #TODO get the details from db and pass to donation details.html
  tmp = slice_dict(ran_a,ran_b)
  return flask.jsonify(**tmp)


@cache.memoize(timeout=60)
@app.route("/readDB", methods=["GET","POST"])
def readDB():
  #range_a = request.args.get('range_a')
  #range_b = request.args.get('range_b')
  global details
  db = connect_it()
  cursor = db.cursor()
  sql = "select * from all_india_pin_code_all_india_pin_code limit 50"
  # Execute the SQL command
  cursor.execute(sql)
  results = cursor.fetchall()
  details = {}
  listt = []
  for row in results:
      rec = {}
      rec['officename'] = row[0]
      rec['pincode'] = row[1]
      rec['officeType'] = row[2]
      rec['Deliverystatus'] = row[3]
      rec['divisionname'] = row[4]
      rec['regionname'] = row[5]
      rec['circlename'] = row[6]
      rec['Taluk'] = row[7]
      rec['Districtname'] = row[8]
      rec['statename'] = row[9]
      listt.append(rec)
  #print a[0]
  details["records"] = listt
  details["total"] = len(details["records"])
  db.close()
  return flask.jsonify(**details)

@app.route("/dbInsertion", methods=["GET","POST"])
def db_call():
  #range_a = request.args.get('range_a')
  #range_b = request.args.get('range_b')
  db = connect_it()
  cursor = db.cursor()
  f = open('all_india_pin_code.csv', 'rt')
  try:
          reader = unicode_csv_reader(f)
          for row in reader:
            sql = "INSERT INTO directory(officename ,pincode,officeType,Deliverystatus,divisionname,regionname,circlename,Taluk,Districtname,statename) VALUES ('%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
            try:
                # Execute the SQL command
                cursor.execute(sql)
                # Fetch all the rows in a list of lists.
                # Now print fetched result
            except:
                db.rollback()
            # disconnect from server
          db.commit()
          db.close()   
  finally:
          f.close()
  
  
  return "Successfully inserted into db: "

if __name__ == "__main__":
	app.run(debug=True)
