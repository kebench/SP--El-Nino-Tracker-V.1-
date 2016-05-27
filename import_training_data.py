#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import csv
import codecs
import MySQLdb
from db_account import db

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, delimiter = "|", **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def insert_to_table(category):
	print "reading"+ str(category) +".txt file"
	f = codecs.open("corpora/"+category+".txt",'rb',encoding="utf-8")
	reader = unicode_csv_reader(f)
	try:
		#variables to be used for insertion
		for row in reader:
			insert_sql = "INSERT INTO test_data (text,category) VALUES ( %s, %s)"
			cursor.execute(insert_sql,(row[0].encode("utf-8"),category))	
		try:
			print "Committing"
			db.commit()
		except:
			db.rollback()
	except csv.Error, e:
		sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
	return

cursor = db.cursor()
db_sql = "CREATE DATABASE IF NOT EXISTS sp_data CHARACTER SET utf8"
cursor.execute(db_sql);
cursor.execute("USE sp_data")
#create table for training data
table_sql = """CREATE TABLE IF NOT EXISTS test_data(
        id int(11) NOT NULL AUTO_INCREMENT,
        text TEXT,
        category VARCHAR(50),
		PRIMARY KEY (id)
        )CHARACTER SET=utf8""" 
cursor.execute(table_sql)
insert_to_table("positive")
insert_to_table("negative")
db.close()

#close database connection