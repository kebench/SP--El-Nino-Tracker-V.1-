#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import nltk
import cPickle
import pprint
import itertools
from nltk import bigrams
from nltk.corpus import stopwords
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.collocations import BigramCollocationFinder
from sklearn.naive_bayes import MultinomialNB,BernoulliNB

class SentimentAnalyzer:
	__tweets = []
	__positive = []
	__negative = []
	__word_features = []
	__training_set = []
	classifier = ""
	MNB_classifier = None
	stop_words = stopwords.words('english') + ["nga","lol","huhu","tas","nya","muna","baka","kang","cant","ngang","omg","ugh","akong","silang","tayong","kung","pang","mga","ano","okay","yan","mas","lang","yung","aww","pag","rin","din","ang","daw","raw","ako","pala","siya","sila","tayo","kasi","man","kayong","kayo","niyo","nyo","nung","ito","itong","kay","nang","kasing","akin","palang"]
	
	def __init__(self):
		"Initialize, contains tuple for classifier"
		self.MNB_classifier = SklearnClassifier(MultinomialNB())
		return
	
	def set_data(self,p,n):
		self.__positive = p
		self.__negative = n
		self.tokenize_tweets()
		self.__word_features = self.get_word_features(self.get_words_in_tweets())
		self.__training_set = nltk.classify.apply_features(self.extract_features, self.__tweets)
		return
	
	def train_data(self):
		self.MNB_classifier.train(self.__training_set)
		#self.classifier = nltk.NaiveBayesClassifier.train(self.__training_set)
		#self.classifier.show_most_informative_features(100)
		#print self.MNB_classifier.classify(self.extract_features(self.tokenize(unicode("halo halo","utf-8"))))
		#print self.classifier.classify(self.extract_features(self.tokenize(unicode("Bakit naman ako, may load pa. Mainit","utf-8"))))
		classifier_file = open("sp_classifier.pkl","wb")
			#cPickle.dump(self.classifier,classifier_file)
		cPickle.dump(self.MNB_classifier,classifier_file)
		classifier_file.close()
		return
	
	def extract_features(self, documents):
		document_words = set(documents)
		features = {}
		
		#for unigram bag of words
		#for word in self.__word_features:
		#	features["contains(%s)" %word] = (word in document_words)
			#features[word] = (word in document_words)
		#for bigram bag of words
		for ngram in itertools.chain(self.__word_features,document_words):
			features[ngram] = (ngram in document_words) 
		return features
	
	def tokenize_tweets(self):
		#split the positive and negative tweets excluding the words that less than two letters
		for (words, sentiment) in self.__positive + self.__negative:
			words_ = []
			count = 0
			for e in words.split():
				translate_table = dict((ord(char), u"") for char in u'!"$%&\'()*+,./:;<=>?@[\\]^_`{|}~')
				words_.append(e.translate(translate_table))
			words_filtered = [e.lower() for e in words_ if ( len(e) >= 3 or e.lower() == "el" or e.lower() == "di" )]
			words_filtered = [e for e in words_filtered if e not in self.stop_words]
			words_filtered = list(bigrams(words_filtered))
			self.__tweets.append((words_filtered, sentiment))
		return
		
	def tokenize(self,text):
		#split the positive and negative tweets excluding the words that less than two letters
		s = []
		for e in text.split():
			translate_table = dict((ord(char), u"") for char in u'!"$%&\'()*+,./:;<=>?@[\\]^_`{|}~')
			s.append(e.translate(translate_table))
		s = [e.lower() for e in s if ( len(e) >= 3 or e.lower() == "el" )]
		s = [e for e in s if e not in self.stop_words]
		s = bigrams(s)
		return s
	
	
	def get_words_in_tweets(self):
		all_words = []
		
		for (words,sentiment) in self.__tweets:
			all_words.extend(words)
			
		return all_words
		
	def get_word_features(self,wordlist):
		wordlist = nltk.FreqDist(wordlist)
		word_features = wordlist.keys()	
		return word_features
		
	def get_training_data(self):
		self.MNB_classifier = None
		classifier_file = open("sp_classifier.pkl","rb")
		self.MNB_classifier = cPickle.load(classifier_file)
		#print("MultinomialNB_classifier accuracy percent:", (nltk.classify.accuracy(self.MNB_classifier, self.__training_set))*100)
		#self.classifier = cPickle.load(classifier_file)
		classifier_file.close()
		return
	