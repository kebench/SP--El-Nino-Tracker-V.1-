import MySQLdb #to be used later
from db_account import db

positive_tweets = []
negative_tweets = []	
	
cursor = db.cursor()
cursor.execute("USE sp_data")

print "Gathering the data"

sql = "SELECT * FROM test_data"
try:
	cursor.execute(sql)
	rows = cursor.fetchall()
except:
	print "Error accessing the data"
	
for row in rows:
	text = row[1]
	category =  row[2]
	
	if category == "positive":
		positive_tweets.append((text,category))
	elif category == "negative":
		negative_tweets.append((text,category))