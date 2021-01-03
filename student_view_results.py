import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import numpy as np
import hashlib


app = Flask(__name__)

# Random login values for mySQL, this will need to be changed for your own machine
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'chy190354890'
app.config['MYSQL_DB'] = 'covidtest_fall2020'
# This code assumes you've already instantiated the DB

mysql = MySQL(app)

