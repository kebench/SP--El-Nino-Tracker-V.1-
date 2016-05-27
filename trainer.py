# Trainer for the El Nino Tracker
# This file is used to train data for the el nino tracker applicaiton
from sentiment_analyzer import SentimentAnalyzer
from training_data import positive_tweets,negative_tweets

analyzer = SentimentAnalyzer()
analyzer.set_data(positive_tweets,negative_tweets)
print "data set"
print "training data..."
analyzer.train_data()
print "Finished training data. Training data is saved in sp_classifier.pickle file"

