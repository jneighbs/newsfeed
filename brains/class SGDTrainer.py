import pickle
import os
from stemming.porter2 import stem
from sklearn.linear_model import SGDClassifier
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt

class SGDTrainer:
	def __init__(self):
		self.topics = ['entertainment', 'sports','foreign','national','politics','business','technology','science','health','arts','fashion','travel']
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
		return

	def trainClassifierForTopic(self, topicToTrain):
		if topicToTrain not in self.topics:
			return

		classifier = self.openClassifier(topicToTrain)
		print type(classifier)

		for topic in self.topics:
			print topic
			if topic == topicToTrain:
				classifier = self.trainClassifier(classifier, topic, 1)
			else:
				classifier = self.trainClassifier(classifier, topic, 0)

		try:
			joblib.dump(classifier, "%s_classifier/%sClassifier.pkl" % (topicToTrain, topicToTrain))
		except:
			return
		
	def trainClassifier(self, classifier, topic, label):
		print "train classifier", type(classifier)
		
		examples = []
		labels = []
		filepath = self.dataDir + topic + '/'
		count = 0

		for file in os.listdir(filepath):
			if file.endswith('.p'):
				nextExample = self.getDocText(filepath + file)
				if nextExample is not '':
					examples.append(nextExample)
					labels.append(label)
					count += 1	

			if count == 100:
				classifier = self.trainClassifierPartial(classifier, examples, labels)
				examples = []
				labels = []
				count = 0
		classifier = self.trainClassifierPartial(classifier, examples, labels)

		return classifier
		#try:
		#	joblib.dump(classifier, "%sClassifier.pkl" % topic)
		#except:
		#	print "Oh fuck, couldn't save classifier..."
		#	return

	def trainClassifierPartial(self, classifier, examples, labels):
		if len(examples) == 0:
			return classifier
		vec = CountVectorizer(tokenizer=self.tokenize, stop_words=self.stopwords, vocabulary=self.vocabulary)
		print len(examples)
		data = vec.fit_transform(examples)
		classifier.partial_fit(X=data, y=labels, classes=[0,1])
		return classifier
			
	def getDocText(self, filepath):
		try:
			article = pickle.load(open(filepath, 'rb'))
		except pickle.UnpicklingError:
			return ''
		return article['text']


	def openClassifier(self, topic):
		try:
			classifier = joblib.load("%s_classifier/%sClassifier.pkl" % (topic, topic))
		except:
			print "No classifier, creating a new one..."
			classifier = SGDClassifier(loss="hinge", penalty="l2")
		return classifier

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

	def quickAndDirty(self):
		keywords = ['score', 'win', 'lose', 'player', 'loss', 'defeat', 'victory', 'points', 'goals', 'run', 'point', 'goal', 'touchdown', 'fieldgoal']
		topics = ['sports', 'politics']

		for topic in topics:

			counts = []
			
			filepath = './classifier_guts/raw_pickles/%s/' % topic

			for file in os.listdir(filepath):
				if file.endswith('.p'):
					text = self.getDoctText(filepath + file)
					words = set(text.split())
					kwCount = 0.0
					for kw in keywords:
						if kw in words:
							kwCount += 1.0
					counts.append(kwCount / len(keyWords))
			plt.hist(counts)



trainer = SGDTrainer()
#trainer.trainClassifierForTopic('science')
#trainer.testOnFile('sports', 'test.txt')
#trainer.testOnFile('sports', 'test2.txt')
#trainer.testOnFile('sports', 'test3.txt')
#trainer.testOnFile('sports', 'test4.txt')
#trainer.testOnTraining('sports', 'science')
#trainer.testOnTraining('sports', 'sports')
trainer.quickAndDirty()





