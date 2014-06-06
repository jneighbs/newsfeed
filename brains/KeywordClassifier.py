import pickle
import os
from stemming.porter2 import stem

# Uncomment this last one if you wanna use .analyze()
#import matplotlib.pyplot as plt

# A simple classifier that uses a set of keywords to determine whether
# a string belongs to a particular topical class or not.
#
# Primary method of interest is classify
# 
# Adjustables:
# - threshold: determines how many keywords or keywords instances need to appear
#	in a document for it to be classified as a particular topic.
# - Boolean Mode: when in this mode, word counts are ignored and the simple presence
#	or absence of keywords in the document is used.
class KeywordClassifier:
	def __init__(self):
		self.topics = ['sports','foreign','national','politics','business','technology','science','health','arts','fashion','travel']

		self.stopwords = set()
		with open('./classifier_guts/stopwords.txt', 'r') as f:
			for line in f:
				line = line.strip()
				self.stopwords.add(line)

		self.threshold = 20
		self.booleanMode = False

		self.topicKeywords = {}
		for topic in self.topics:
			self.topicKeywords[topic] = self.loadKeywords(topic)

		return

	###################################################
	# Usage:										  #
	# from KeywordClassifier import KeywordClassifier #
	# clf = KeywordClassifier()                       #
	# clf.classify(articleText, 'sports')             #
	###################################################
	
	# Does exactly what you'd expect it to.
	# Returns True or False.
	def classify(self, text, topic):
		if topic not in self.topics:
			return False

		words = text.split()
		words = self.cleanText(words)
		if self.booleanMode:
			words = set(words)
		keywords = set(self.topicKeywords[topic])

		kwCount = 0
		for word in words:
			if word in keywords:
				kwCount += 1
		
		return kwCount >= self.threshold

	# For each topic, find the maxResults most frequent words and the maxResult
	# words whose frequency in topical documents has the greatest positive difference
	# from all other documents, add to those any manually selected bonus words,
	# and save everything to some text files.
	#
	# You should only use this if you need to reset our list of keywords.
	# NB: If you do so, you should manually go through the resulting .txt files
	# and prune common, garbage words that might've made it through the stopwords
	# filtering.
	def scrapeWords(self, maxResults):
		bonusWords = {}
		bonusWords['foreign'] = ['intervention', 'invasion', 'war', 'diplomat', 'UN', 'EU', 'military']
		bonusWords['sports'] = ['score', 'win', 'lose', 'player', 'loss', 'defeat', 'victory', 'points', 'goals', 'run', 'point', 'goal', 'touchdown', 'fieldgoal', 'pitch', 'pitcher', 'NBA', 'basketball', 'MLB', 'baseball', 'NFL', 'football', 'soccer', 'hockey', 'NHL']
		bonusWords['politics'] = ['representative', 'president', 'senator', 'senate', 'election', 'vote', 'votes', 'voter', 'filibuster', 'legislation', 'bill', 'reform', 'conservative', 'republican', 'liberal', 'democrat']
		bonusWords['business'] = ['negotiate', 'payroll', 'revenue', 'profit', 'strategy', 'stock', 'dividend', 'negotiate', 'hire', 'HR', 'sell']
		for topic in self.topics:
			freqWords = self.mostFrequent(topic, maxResults)
			relFreqWords = self.mostFrequent(topic, maxResults)
			keywords = set(freqWords).union(set(relFreqWords))

			if topic in bonusWords:
				keywords = keywords.union(set(bonusWords[topic]))
			keywords = list(keywords)
			keywords = self.cleanText(keywords)
			print topic
			print keywords
			print ""

			self.saveWords(keywords, topic)

	###################################################
	# THESE											  #
	# ARE 											  #
	# BASICALLY										  #
	# ALL 											  #
	# PRIVATE 										  #
	###################################################

	# Save the keywords for a specific topic in a .txt file
	def saveWords(self, words, topic):
		filepath = './classifier_guts/keywords/%s.txt' % topic
		with open(filepath, 'w') as f:
			for word in words:
				f.write('%s\n' % word)

	# Load the keywords for a specific topic.
	def loadKeywords(self, topic):
		words = []
		filepath = './classifier_guts/keywords/%s.txt' % topic
		with open(filepath, 'r') as f:
			for line in f:
				line = line.strip()
				words.append(line)
		return words

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
			

	# Turn a list of (frequency, word) tuples
	# into a list of just the words
	def toWordArray(self, freqWordPairs):
		words = []
		for freq, word in freqWordPairs:
			words.append(word)
		return words

	# Unpickle an NYTimes article and get its text
	def getDocText(self, filepath):
		try:
			article = pickle.load(open(filepath, 'rb'))
		except pickle.UnpicklingError:
			return ''
		return article['text']
			

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


	# Print some nice histograms of how many of our keywords we have
	# in each subcorpus for a given topic.
	# NB: You need to uncomment the matplotlib import and have
	# matplotlib / scipy installed for this to work.
	def analyze(self, singleVsRest=False, targetTopic=None):
		
		for topic in self.topics:

			if singleVsRest:
				keywords = self.loadKeywords(targetTopic)
			else:
				keywords = self.loadKeywords(topic)

			if len(keywords) == 0:
				continue

			keywords = set(keywords)

			counts = []
			
			filepath = './classifier_guts/raw_pickles/%s/' % topic

			for file in os.listdir(filepath):
				if file.endswith('.p'):
					text = self.getDocText(filepath + file)
					words = text.split()
					words = self.cleanText(words)
					#words = set(words)
					kwCount = 0.0
					for word in words:
						if word in keywords:
							kwCount += 1
					counts.append(kwCount)

			plt.hist(counts, normed=True, bins=20)
			plt.title(topic)
			plt.show()

clf = KeywordClassifier()
clf.analyze(singleVsRest=True, targetTopic='business')


