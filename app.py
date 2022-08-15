from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import os
#import re
#import logging

app = Flask(__name__)
mysql = MySQL(app)
 
app.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")

censor_replacement = 'XXX'

# Return only data fields and remove SQL commands
remove_list = ['alter', 'create', 'table', 'database', 'select', 'from', 'where', 'in', 'as', 'order', 'group', 'by', 'limit', 'and', 'or', 'insert', 'update', 'inner', 'outer', 'left', 'right', 'join' ]

def censor_data(censor, fields_only, data):
  #Goes through each line in 'data' ..
  # .. and replaces fields in the lines matching data with 'censor_replacement'
  to_censor = censor.split(',')
  counter=-1
  new_data=[]
  for row in data:
    counter = counter+1
    line = data[counter]
    for field in fields_only:
      if field in to_censor:
        bad_index = fields_only.index(field)
        line[bad_index] = censor_replacement
    new_data.insert(counter, line)
  return new_data

def fields_only(query):
  # Remove commas and semicolon from query, split it
  # Example: ['SELECT', 'FirstName', 'LastName', 'from', 'Persons']
  split_query = query.replace(',', ' ').replace(';', '').split()

  # Remove the element after the from
  split_query.pop(split_query.index('from')+1)
 
  # Return only data fields and remove SQL commands
  fields = [x for x in split_query if x.lower() not in remove_list]
  
  return fields

def filter_data(censor, query, data):
  # Convert list of tuples to list of lists
  data_new = [list(x) for x in data]

  return censor_data(censor, fields_only(query), data_new)

def build_new_query_from_description(query, cursor):
  # Describe the table we found in 'query' ..
  # .. and build a new query replacing the star *
  table_name = query.split()[-1].replace(';', '')
  cursor.execute('describe '+ table_name + ';')
  field_list = [ x[0] for x in cursor.fetchall()]
  new_query_fields = ', '.join(field_list)
  new_query = "select " + new_query_fields + ' from ' + table_name + ';'
  return new_query
 
@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
     
    if request.method == 'POST':
        censor = request.form['censor']
        query = request.form['query']

        try:
          cursor = mysql.connection.cursor()
        except Exception:
          return "Cannot make SQL connection", 500	
        else:
          if query:
            if not censor:
              censor = ""
            if '*' in query:
              query = build_new_query_from_description(query, cursor)
            try:
              cursor.execute(query)
              data =  cursor.fetchall()
            except Exception:
              return "Cannot fetch data", 500
            else:
              try:
                data_filtered = filter_data(censor, query, data)
                fields = fields_only(query)
                cursor.close()
              except Exception:
                return "Something went wrong during filtering", 500
              else:
                return render_template('result.html', fields=fields, censor=censor, query=query, data=data_filtered)
          else:
            return "No query provided!", 400
