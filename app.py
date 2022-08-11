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

def censor_data(censor, fields_only, data):
  # Goes through each line in 'data' ..
  # .. and replaces fields in the lines matching data with 'censor_replacement'
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
  
  # Return only data fields and remove SQL commands
  remove_list = ['select', 'from', 'where', 'in', 'as', 'order_by']
  fields = [x for x in split_query if x.lower() not in remove_list]
  return fields

def filter_data(censor, query, data):
  counter = -1
  data_new = ['|'.join(i) for i in data if data]
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
            return "Cannot execute query or connect to SQL", 500
          else:
            try:
              data =  cursor.fetchall()
            except Exception:
              return "Cannot fetch data", 500
            else:
              try:
                data_filtered = filter_data(censor, query, data)
                cursor.close()
              except Exception:
                return "Something went wrong during filtering", 500
              else:
                return render_template('result.html', censor=censor, query=query, data=data_filtered)
        else:
          return "No query provided!", 400
