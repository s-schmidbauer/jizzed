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

#app.config.from_envvar('MYSQL_HOST')
#app.config.from_envvar('MYSQL_USER')
#app.config.from_envvar('MYSQL_PASSWORD')
#app.config.from_envvar('MYSQL_DB')

censor_replacement = 'XXX'

def censor_data(censor, fields_only, data):
  # walks through each line in 'data'
  # and replaces fields in the lines matching data with 'censor_replacement'
  to_censor = censor.split(',')
  counter=-1
  new_data=[]
  for row in data:
    counter = counter+1
    line = data[counter].split('|')
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
  
  # Return only fields and remove SELECT and FROM
  # Example ['FirstName', 'LastName', 'Persons']
  fields = [x for x in split_query if not x.lower().startswith('select') and not x.lower().startswith('from') ]
  return fields

def filter_data(censor, query, data):
  counter = -1
  data_new = ['|'.join(i) for i in data]
  return censor_data(censor, fields_only(query), data_new)
 
@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
     
    if request.method == 'POST':
        censor = request.form['censor']
        query = request.form['query']

        if query:
          if not censor:
            censor = ""
          try:
            cursor = mysql.connection.cursor()
            cursor.execute(query)
          except Exception:
            return "Cannot execute query or connect to SQL", 400
          else:
            try:
              data =  cursor.fetchall()
            except Exception:
              return "Cannot fetch data", 400
            else:
              try:
                data_filtered = filter_data(censor, query, data)
                cursor.close()
              except Exception:
                return "Something went wrong during filtering", 400
              else:
                return render_template('result.html', censor=censor, query=query, data=data_filtered)
        else:
          return "No query and censor found!", 400
