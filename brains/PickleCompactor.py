import pickle
import os
from stemming.porter2 import stem
from sklearn.linear_model import SGDClassifier
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer

class PickleCompactor:
	def __init__(self):
		#self.topics = ['entertainment', 'sports','foreign','national','politics','business','technology','science','health','arts','fashion','travel']
		self.topics = ['politics']
		self.dataDir = './classifier_guts/raw_pickles/'
		self.targetDir = './classifier_guts/counts/'
		self.stopwords = set()
		with open('./classifier_guts/stopwords.txt', 'r') as f:
			for line in f:
				line = line.strip()
				self.stopwords.add(line)

		self.vocabulary = []
		with open('./classifier_guts/terms.txt') as f:
			for line in f:
				line = line.strip()
				self.vocabulary.append(line)
		return

	def compactAllPickles(self):
		for topic in self.topics:
			filepath = self.dataDir + topic + '/'
			count = 0
			failCount = 0
			for file in os.listdir(filepath):
				if file.endswith('.p'):
					try:
						article = pickle.load(open(filepath + file, 'rb'))
						self.compactArticle(article, topic)
						count += 1
					except pickle.UnpicklingError:
						failCount += 1
			print topic, count, failCount

	def feedAllToClassifier(self):
		for topic in self.topics:
			filepath = self.dataDir + topic + '/'
			count = 0

			classifier = self.openClassifier(topic)

			docs = []

			for file in os.listdir(filepath):
				if file.endswith('.p'):
					try:
						article = pickle.load(open(filepath + file, 'rb'))
						count += 1
					except pickle.UnpicklingError:
						continue
				docs.append(article['text'])

				if count == 100:
					classifier = self.feedBatchToClassifier(classifier, docs)
					docs = []
					count = 0
			classifier = self.feedBatchToClassifier(classifier, docs)
			try:
				joblib.dump(classifier, "%sClassifier.pkl" % topic)
			except:
				return

	def openClassifier(self, topic):
		try:
			classifier = joblib.load("%sClassifier.pkl" % topic)
		except:
			classifier = SGDClassifier(loss="hinge", penalty="l2")
		return classifier

	def feedBatchToClassifier(classifier, docs):
		vec = CountVectorizer(tokenizer=self.tokenize, stop_words=self.stopwords, vocabulary=self.vocabulary)
		data = vec.fit_transform(docs)
		classifier.partial_fit()


	def compactBBC(self):
		numProcessed = 0

		with open('./classifier_guts/bbc/bbc.mtx', 'r') as f:


			for line in f:
				termId, docId, count = line.split()
				termId = int(termId.strip())
				docId = int(docId.strip())
				count = int(count.strin())

	def compactArticle(self, article, topic):

		countList = []

		cleanedText = self.cleanText(article['text'])

		countDict = self.buildCountDict(cleanedText)
		
		with open('./classifier_guts/terms.txt', 'r') as f:
			termId = 0

			# Handle the terms already in our terms list
			for line in f:
				term = line.strip()
				if term in countDict:
					countList.append((termId, countDict[term]))
					del countDict[term]

				termId += 1

		# And the ones not in it yet.
		with open('./classifier_guts/terms.txt', 'a') as f:
			for term, count in countDict.items():
				term = stem(term)
				try:
					f.write(term + '\n')
					countList.append((termId, count))
					termId += 1
				except:
					print "couldn't write term ", term

		filename = article['headline'] + article['pub_date'] + '.p'
		#try:
		#	pickle.dump(countList, open(self.targetDir + topic + '/' + filename, "wb" ))
		#except pickle.PicklingError:
		#	print "failed to pickle", filename

	def cleanText(self, textStr):
		cleanedText = []
		words = textStr.split()
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

	def tokenize(self, text):
		words = text.split()
		for word in words:
			word = word.lower()
			word = ''.join(ch for ch in word if ch.isalnum())
			word = stem(word)
		return ' '.join(words)

	def buildCountDict(self, text):
		counts = {}
		for word in text:
			counts[word] = counts.get(word, 0) + 1
		return counts




pc = PickleCompactor()
#pc.compactAllPickles()