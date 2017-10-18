import json
import os
import re

from flask import Flask,redirect
from flask import render_template
import psycopg2 as dbapi2 
from flask.helpers import url_for



app = Flask(__name__)


def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn


@app.route('/')
def home_page():
    return "Hello"


@app.route('/initdb')
def initialize():
   with dbapi2.connect(app.config['dsn']) as connection:
      cursor = connection.cursor()
      query = """DROP TABLE IF EXISTS COUNTER"""
      cursor.execute(query)
      query = """CREATE TABLE COUNTER (N INTEGER)"""
      cursor.execute(query)
      query = """INSERT INTO COUNTER(N)VALUES(0)"""
      cursor.execute(query)
      connection.commit()
   return redirect(url_for('home_page'))   

@app.route('/count')
def counter_pagge():
   with dbapi2.connect(app.config['dsn']) as connection:
      cursor = connection.cursor()
      query = "UPDATE COUNTER SET N = N + 1"
      cursor.execute(query)
      connection.commit()

      query = "SELECT N FROM COUNTER"
      cursor.execute(query)
      count = cursor.fetchone()[0]
      return "This page was accessed %d times " % count






# example use for a Flask app:
if __name__ == '__main__':

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='rsltgy' password='123456'
                               host='localhost' port=5432 dbname='itu/labs'"""

    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)


