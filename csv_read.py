#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import csv
import MySQLdb #import the library to connect to mysql database
a = 0
#open connection to db
db = MySQLdb.connect(user = "kebench",passwd = "k3b3nch0$")
#prepare a cursor
cursor = db.cursor()
#create database
db_sql = "CREATE DATABASE IF NOT EXISTS sp_data CHARACTER SET utf8"
cursor.execute(db_sql);
cursor.execute("USE sp_data")
#create table for test cases
table_sql = """CREATE TABLE IF NOT EXISTS test_cases(
        id int(11) NOT NULL AUTO_INCREMENT,
        text TEXT,
        coordinates GEOMETRY,
        created_at VARCHAR(50),
        screen_name VARCHAR(50),
        country_code VARCHAR(2),
        lang VARCHAR(5),
        PRIMARY KEY (id)
        )CHARACTER SET=utf8"""
cursor.execute(table_sql)
for num in range(1,9):	
	#read the csv
	i = str(num)
	print ("reading sp_num",i)
	f = open('sp_'+i+'.csv','rb')
	reader = csv.DictReader(f)
    #try reading every row of the file
	try:
        #variables to be used for insertion
		lat = lon = 0
		text = date = name = ""
		counter = 1
        #traverse every row and save into database
		for row in reader:
            #check if lat and lon are set else, use the location coordinates
			if row["lat"] != "NA" or row["lon"] != "NA":
                #print (row[""],row["lat"],row["lon"])
				lat = float(row["lat"])
				lon = float(row["lon"])
			elif row["place_lat"] != "NA" or row["place_lon"] != "NA":
				lat = float(row["place_lat"])
				lon = float(row["place_lon"])

			text = row["text"]
			date = row["created_at"]
			name = row["screen_name"]
			country = row["country_code"]
			lang = row["lang"]
            #try saving to the database
			try:
                #lat = x, long = y, point x,y
				if (( row["lang"] == "en" or row["lang"] == "tl" ) and row["country_code"] == "PH" and (lat > 0 or lon > 0)):
					a += 1
					print (i," inserting row",a)
					counter += 1
					insert_sql = "INSERT INTO test_cases (text,coordinates,created_at,screen_name,country_code,lang) VALUES ( %s, GeomFromText('POINT(%s %s)'),%s,%s,%s,%s)"
					cursor.execute(insert_sql,(text,lat,lon,date,name,country,lang))
				
				if counter == 1000:
					print "Committing to DB"
					db.commit()
					counter = 1
			except:
				db.rollback()
		try:
			print "Committing, not 1k though"
			db.commit()
			counter = 1
		except:
			db.rollback();
	except csv.Error, e:
		sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
#close database connection
db.close()
