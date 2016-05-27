#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#My Libraries 
from db_account import db
from sentiment_analyzer import SentimentAnalyzer
#External Lib/3rd Party Libs
from threading import Thread
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
from training_data import positive_tweets,negative_tweets
import time
import pprint
import csv
import json

async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

print('async_mode is ' + async_mode)

import eventlet
eventlet.monkey_patch()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

cursor = db.cursor()
cursor.execute("USE sp_data")

analyzer = SentimentAnalyzer()
analyzer.set_data(positive_tweets,negative_tweets)
#analyzer.train_data()
analyzer.get_training_data()
	
tweet_query = "SELECT text, ST_X(coordinates) AS lat, ST_Y(coordinates) AS lon, created_at, country_code, lang FROM test_cases"

try:
	cursor.execute(tweet_query)
	test_tweets = cursor.fetchall()
	print "Executing SQL statement"
except:
	print "Error: cannot fetch data!"
	
def do_analysis():
	tweet = { "text": "", "lat": 0, "lon": 0, "created_at": "", "country_code": 0, "lang": "" }
	data_to_be_sent = {}
	count = 1
	tweet_count_positive = 0;
	first_sent = False;
	positives = []
	dates_of_positive = dict()
	dates_of_tweets = dict()
	while True:
		#pprint.pprint(analyzer.extract_features(analyzer.tokenize("init")))
		#pr = analyzer.BNB_classifier.classify(analyzer.extract_features(analyzer.tokenize("ang init")))
		for row in test_tweets:
			tweet["text"] = row[0]
			tweet["lat"] = row[1]
			tweet["lon"] = row[2]
			tweet["created_at"] = row[3][4:10]
			tweet["country_code"] = row[4]
			tweet["lang"] = row[5]
			
			if tweet["created_at"] in dates_of_tweets:
				dates_of_tweets[tweet["created_at"]] += 1
			else:
				dates_of_tweets[tweet["created_at"]] = 1
			
			#do sentiment analysis
			pr = analyzer.MNB_classifier.classify(analyzer.extract_features(analyzer.tokenize(tweet["text"])))
			if pr == "positive":
				data_to_be_sent["data"+`count`] = {}
				data_to_be_sent["data"+`count`]["lat"] = tweet["lat"]
				data_to_be_sent["data"+`count`]["lon"] = tweet["lon"]
				data_to_be_sent["data"+`count`]["text"] = tweet["text"]
				count += 1
				
				if tweet["created_at"] in dates_of_positive:
					dates_of_positive[tweet["created_at"]] += 1
				else:
					dates_of_positive[tweet["created_at"]] = 1
				
				tweet_count_positive += 1
				#positives.append(tweet["text"]+'\r\n') 
				print str(tweet["text"]) + " [Current tweet count:" + str(count)+ " Current positive tweet: "+ str(tweet_count_positive) + "]"
			#if len(data_to_be_sent) >= 10:
				socketio.emit('track',
					json.dumps(data_to_be_sent),
					namespace='/el_nino_tracker')
				#count = 1
				data_to_be_sent = {}
				time.sleep(1)
			#if true get the trending topics in regards to el nino"""\
			if( first_sent == False ):
				first_sent = True
				time.sleep(5)
			#print str(pr) + ' ' + str(tweet["text"])
		#f = open("positives_MNB.txt","wb")
		#for e in positives:
		#	f.write(str(e))
		#f.close()
		break
	
	#This will send the remaining tweets after it exhausts all of the data
	data_to_be_sent["last_count"] = True
	data_to_be_sent["tweet_count"] = tweet_count_positive
	socketio.emit('track',
		json.dumps(data_to_be_sent),
		namespace='/el_nino_tracker')
	print("Number of positive tweets:",tweet_count_positive)
	pprint.pprint(dates_of_tweets)
	pprint.pprint(dates_of_positive)
	
	f = open('dates_positive.csv','wb')
	w = csv.DictWriter(f,dates_of_positive.keys())
	w.writerow(dates_of_positive)
	f.close()
	
	k = open('dates_all.csv','wb')
	w = csv.DictWriter(k,dates_of_positive.keys())
	w.writerow(dates_of_tweets)
	k.close()
	
	first_sent = False;
	
@socketio.on_error('/el_nino_tracker')
def error_handler_chat(e):
	print e
	pass

@app.route('/')
def index():
	global thread
	if thread is None:
		thread = Thread(target=do_analysis)
		thread.daemon = True
		thread.start()
	return render_template('index.html')
		 
@socketio.on('connect', namespace='/el_nino_tracker')
def test_connect():
    emit('log', {'data': 'Connected', 'count': 0})
	
@socketio.on('disconnect', namespace='/el_nino_tracker')
def test_disconnect():
    print('Client disconnected', request.sid)
	
if __name__ == '__main__':
   socketio.run(app, debug=True)

db.close()