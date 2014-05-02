import pickle
import os
from stemming.porter2 import stem
from sklearn.linear_model import SGDClassifier
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt

class SGDTrainer:
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
		keywords = ['score', 'win', 'lose', 'player', 'loss', 'defeat', 'victory', 'points', 'goals', 'run', 'point', 'goal', 'touchdown', 'fieldgoal', 'pitch', 'pitcher', 'NBA', 'basketball', 'MLB', 'baseball', 'NFL', 'football', 'soccer', 'hockey', 'NHL']
		bonusWords = ['noted.', 'scored', 'coach', 'beat', 'win', 'tournament', 'three', 'second', 'game', 'york', 'news', 'world', 'league', 'basketball', 'two', 'will', 'players', 'victory', 'team', 'final']
		keywords.extend(bonusWords)
		#keywords = ['representative', 'president', 'senator', 'senate', 'election', 'vote', 'votes', 'voter', 'filibuster', 'legislation', 'bill', 'reform', 'conservative', 'republican', 'liberal', 'democrat']
		#keywords = ['negotiate', 'payroll', 'revenue', 'profit', '']
		topics = ['sports', 'politics', 'business', 'foreign', 'fashion']

		for topic in topics:

			counts = []
			
			filepath = './classifier_guts/raw_pickles/%s/' % topic

			for file in os.listdir(filepath):
				if file.endswith('.p'):
					text = self.getDocText(filepath + file)
					words = set(text.split())
					kwCount = 0.0
					for kw in keywords:
						if kw in words:
							kwCount += 1.0
					counts.append(kwCount / len(keywords))

			plt.hist(counts, normed=True)
			plt.title(topic)
			plt.show()

	def quickAndDirtyII(self, targetTopic, maxResults=23):
		freqWords = self.mostFrequent(targetTopic, maxResults)
		relFreqWords = self.mostFrequent(targetTopic, maxResults)
		keywords = set(freqWords).union(set(relFreqWords))
		keywords = list(keywords)
		print keywords

		for topic in self.topics:
			print topic

			counts = []
			
			filepath = './classifier_guts/raw_pickles/%s/' % topic

			for file in os.listdir(filepath):
				if file.endswith('.p'):
					text = self.getDocText(filepath + file)
					words = set()
					for word in text.split():
						word = word.lower()
					try:
						word = word.encode('ascii')
					except UnicodeEncodeError:
						continue
					words.add(word)	
					kwCount = 0.0
					for kw in keywords:
						if kw in words:
							kwCount += 1.0
					counts.append(kwCount / len(keywords))
			if len(counts) == 0:
				print "couldn't find any matches for", topic
				continue
			plt.hist(counts)
			plt.title(topic)
			plt.show()

	def scrapeWords(self, maxResults):
		for topic in self.topics:
			freqWords = self.mostFrequent(topic, maxResults)
			relFreqWords = self.mostFrequent(topic, maxResults)
			keywords = set(freqWords).union(set(relFreqWords))
			keywords = list(keywords)
			print topic
			print keywords
			print ""
			

	def toWordArray(self, freqWordPairs):
		words = []
		for freq, word in freqWordPairs:
			words.append(word)
		return words
			

	# Get the maxResults most frequent words in our corpus for a given topic.
	def mostFrequent(self, topic, maxResults=15):
		counts = {}
		filepath = './classifier_guts/raw_pickles/%s/' % topic
		for file in os.listdir(filepath):
			if file.endswith('.p'):
				text = self.getDocText(filepath + file)
				words = text.split()
				for word in words:
					word = word.lower()
					try:
						word = word.encode('ascii')
					except UnicodeEncodeError:
						continue
					if word not in self.stopwords:
						counts[word] = counts.get(word, 0) + 1
		freqs = []
		for word, count in counts.items():
			freqs.append((count, word))
		freqs.sort()
		freqs.reverse()
		#print freqs[:maxResults]
		return self.toWordArray(freqs[:maxResults])


	# Get the maxResults words which have the greatest difference between their
	# frequency within the documents for a given topic and all the documents.
	def relFrequency(self, topic, maxResults=15):
		overallCounts = {}
		overallTotal = 0.0
		topicalCounts = {}
		topicalTotal = 0.0
		for currTopic in self.topics:
			filepath = './classifier_guts/raw_pickles/%s/' % currTopic
			for file in os.listdir(filepath):
				if file.endswith('.p'):
					text = self.getDocText(filepath + file)
					words = text.split()
					for word in words:
						word = word.lower()
						try:
							word = word.encode('ascii')
						except UnicodeEncodeError:
							continue
						if word not in self.stopwords:
							overallCounts[word] = overallCounts.get(word, 0) + 1
							overallTotal += 1
							if currTopic == topic:
								topicalCounts[word] = topicalCounts.get(word, 0) + 1
								topicalTotal += 1
		freqDiffs = []
		for word, count in overallCounts.items():
			if word in topicalCounts:
				try:
					freqDiff = topicalCounts[word] / topicalTotal - count / overallTotal
					freqDiffs.append((freqDiff, word))
				except:
					print word, count, topicalCounts[word], overallTotal, topicalTotal
		freqDiffs.sort()
		freqDiffs.reverse()
		#print freqDiffs[:maxResults]
		return self.toWordArray(freqDiffs[:maxResults])



trainer = SGDTrainer()
#trainer.trainClassifierForTopic('science')
#trainer.testOnFile('sports', 'test.txt')
#trainer.testOnFile('sports', 'test2.txt')
#trainer.testOnFile('sports', 'test3.txt')
#trainer.testOnFile('sports', 'test4.txt')
#trainer.testOnTraining('sports', 'science')
#trainer.testOnTraining('sports', 'sports')
trainer.quickAndDirty()
#print trainer.mostFrequent('sports')
#print trainer.relFrequency('sports')
#trainer.scrapeWords(20)



