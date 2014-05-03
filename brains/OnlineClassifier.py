import pickle
import os
from stemming.porter2 import stem
from sklearn.linear_model import SGDClassifier
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer

# A bundle of SGD linear classifiers, one for each news topic.
# Can be trained on a big 'ole pile of pickled NYTimes article snippets,
# or update one example at a time.

class OnlineClassifier:
	def __init__(self):
		self.topics = ['sports','foreign','national','politics','business','technology','science','health','arts','fashion','travel']
		#self.topics = ['politics']

		self.dataDir = './classifier_guts/raw_pickles/'
		self.targetDir = './classifier_guts/counts/'

		self.stopwords = set()
		with open('./classifier_guts/stopwords.txt', 'r') as f:
			for line in f:
				line = line.strip()
				self.stopwords.add(line)

		self.vocabulary = set()
		with open('./classifier_guts/terms.txt') as f:
			for line in f:
				line = line.strip()
				self.vocabulary.add(line)

		self.exampleStack = {}
		for topic in self.topics:
			self.exampleStack[topic] = []
		self.exampleStackLimit = 1
		return

	# Create a new classifier for the given topic, train it,
	# and replace the old one with it
	def resetTopicClassifier(self, topicToTrain):
		if topicToTrain not in self.topics:
			return

		classifier = SGDClassifier(loss="hinge", penalty="l2")

		self.trainClassifierInternal(classifier, topicToTrain)

	def fullReset(self):
		for topic in self.topics:
			self.resetTopicClassifier(topic)

	# Train alinear SGD classifier for a particular topic.
	# Pickles the classifier in its directory.
	def trainTopicClassifier(self, topicToTrain):
		if topicToTrain not in self.topics:
			return

		classifier = self.openClassifier(topicToTrain)

		self.trainClassifierInternal(classifier, topicToTrain)

	# Give the classifier another training example and label to train
	# on. Classifier keeps a stack of examples and only actually updates
	# once there are exampleStackLimit number of examples in the stack
	# for that topic's classifier.
	def addTrainingExample(self, example, topic, label):
		if topic not in self.topics:
			return
		if label != 0 and label != 1:
			return
		if type(example) != type("yummy dummy") or len(example) == 0:
			return
		
		self.exampleStack[topic].append((example, label))

		if len(self.exampleStack[topic]) >= self.exampleStackLimit:
			self.updateClassifierFromStack(topic)



	###################################################
	#												  #
	# Utility Functions of Dubious Utility			  #
	#												  #
	###################################################

	# Test the classifier on a file. File expected to contain only text, 
	# nothing crazy.
	def testOnFile(self, topic, filepath):
		if topic not in self.topics:
			return
		classifier = self.openClassifier(topic)

		text = ""
		with open(filepath, 'r') as f:
			for line in f:
				text += line
		vec = CountVectorizer(tokenizer=self.tokenize, stop_words=self.stopwords, vocabulary=self.vocabulary)
		data = vec.fit_transform([text])
		return classifier.predict(data)[0]

	# Test a particular topic classifier on all the pickled NYTimes data.
	def testOnTraining(self, topic, classifierTopic):
		if topic not in self.topics:
			return
		total = 0
		correct = 0
		classifier = self.openClassifier(classifierTopic)
		filepath = './classifier_guts/raw_pickles/%s/' % topic
		for file in os.listdir(filepath):
			if file.endswith('.p'):	
				text = self.getDocText(filepath + file)
				vec = CountVectorizer(tokenizer=self.tokenize, stop_words=self.stopwords, vocabulary=self.vocabulary)
				data = vec.fit_transform([text])
				correct += classifier.predict(data)[0]
				total += 1
		print float(correct) / total

	###################################################
	# THESE											  #
	# ARE 											  #
	# BASICALLY										  #
	# ALL 											  #
	# PRIVATE 										  #
	###################################################

	# Train the a classifier for the given topic.
	# Uses the given topic's documents as positive examples,
	# and all others as negative ones.
	def trainClassifierInternal(self, classifier, topicToTrain):
		print "TRAINING %s CLASSIFIER" % topicToTrain.upper()
		for topic in self.topics:
			print "training on %s examples" % topic
			if topic == topicToTrain:
				classifier = self.trainClassifierOnTopic(classifier, topic, 1)
			else:
				classifier = self.trainClassifierOnTopic(classifier, topic, 0)

		try:
			joblib.dump(classifier, "%s_classifier/%sClassifier.pkl" % (topicToTrain, topicToTrain))
			print "FINISHED TRAINING %s CLASSIFIER" % topicToTrain.upper()
		except:
			print "COULD NOT SAVE %s CLASSIFIER O____o" % topicToTrain.upper()
			return
	
	# For all example documents for a particular topic, feeds them to the
	# SGD classifier. Label=1 means that topic is the topic of the classifier
	# we're training. Label=0 means that the topic is a different topic
	# e.g. topic='business' and we're training the sports classifier.
	def trainClassifierOnTopic(self, classifier, topic, label):
		
		examples = []
		labels = []
		filepath = self.dataDir + topic + '/'
		count = 0
		total = 0

		for file in os.listdir(filepath):
			if file.endswith('.p'):
				nextExample = self.getDocText(filepath + file)
				if nextExample is not '':
					examples.append(nextExample)
					labels.append(label)
					count += 1	
					total += 1

			if count == 100:
				print total
				classifier = self.ingestExamples(classifier, examples, labels)
				examples = []
				labels = []
				count = 0
		print total
		classifier = self.ingestExamples(classifier, examples, labels)

		return classifier

	# Updates the classifier for the given topic with the stack of examples
	# for that classifier, then saves the updated classifier.
	def updateClassifierFromStack(self, topic):
		classifier = self.openClassifier(topic)
		
		labels = []
		examples = []
		for example, label in self.exampleStack[topic]:
			examples.append(example)
			labels.append(label)

		classifier = self.ingestExamples(classifier, examples, labels)

		try:
			joblib.dump(classifier, "%s_classifier/%sClassifier.pkl" % (topic, topic))
		except:
			print "COULD NOT SAVE %s CLASSIFIER O____o" % topic.upper()
			return

	# Does the actual partial training of the SGD classifier
	def ingestExamples(self, classifier, examples, labels):
		if len(examples) == 0:
			return classifier
		vec = CountVectorizer(tokenizer=self.tokenize, stop_words=self.stopwords, vocabulary=self.vocabulary)
		data = vec.fit_transform(examples)
		classifier.partial_fit(X=data, y=labels, classes=[0,1])
		return classifier

	# Lowercase, remove non alphanumberic characters, stem, and remove
	# stopwords.
	# Takes and returns a list.
	def cleanText(self, words):
		cleanedText = []
		for word in words:
			word = word.lower()
			word = ''.join(ch for ch in word if ch.isalnum())
			word = stem(word)
			if len(word) <= 2:
				continue
			if word in self.stopwords:
				continue
			cleanedText.append(word)
		return cleanedText
			
	# Get the text from a pickled NYTimes article
	def getDocText(self, filepath):
		try:
			article = pickle.load(open(filepath, 'rb'))
		except pickle.UnpicklingError:
			return ''
		return article['text']

	# Attempts to open a pickled classifier. If not found, creates a new one.
	def openClassifier(self, topic):
		try:
			classifier = joblib.load("%s_classifier/%sClassifier.pkl" % (topic, topic))
		except:
			print "No classifier, creating a new one..."
			classifier = SGDClassifier(loss="hinge", penalty="l2")
		return classifier

	# Splits a string into whitespace-delimited tokens, lowercases them,
	# removes any non-alphanumeric characters, and returns them as an array.
	def tokenize(self, text):
		#print "tokenizing..."
		tokens = []
		words = text.split()
		for word in words:
			word = word.lower()
			word = ''.join(ch for ch in word if ch.isalnum())
			word = stem(word)
			tokens.append(word)
		#print tokens
		return tokens




