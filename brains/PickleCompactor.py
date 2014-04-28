import pickle
import os

class PickleCompactor:
	def __init__(self):
		#self.topics = ['entertainment', 'sports','foreign','national','politics','business','technology','science','health','arts','fashion','travel']
		self.topics = ['politics']
		self.dataDir = './classifier_guts/raw_pickles/'
		self.targetDir = './classifier_guts/counts/'
		return

	def compactAll(self):
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

	def compactArticle(self, article, topic):
		countList = []

		countDict = self.buildCountDict(article)
		
		with open('./classifier_guts/terms.txt') as f:
			termId = 0
			for line in f:
				term = line.strip()
				if term in countDict:
					countList.append((termId, countDict[term]))
					del countDict[term]

				termId += 1
		filename = article['headline'] + article['pub_date'] + '.p'
		try:
			pickle.dump(countList, open(self.targetDir + topic + '/' + filename, "wb" ))
		except pickle.PicklingError:
			print "failed to pickle", filename

	def buildCountDict(self, article):
		counts = {}
		words = article['text'].split(' ')
		for word in words:
			counts[word] = counts.get(word, 0) + 1
		return counts

pc = PickleCompactor()
pc.compactAll()