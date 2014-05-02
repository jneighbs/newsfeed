from nytimesarticle import articleAPI
from time import time
from datetime import datetime
import pickle


api = articleAPI('2aeeb020218af0f30993f12ff451d821:10:62878084')
'''
page = 0
responseObject = api.search( q = '*', fq = {'source':['Reuters','AP', 'The New York Times'], 'news_desk':['travel']}, begin_date = 20140409, page=page)
articles = responseObject['response']['docs']
for article in articles:
	print article['headline']['main']
	print article['news_desk']
'''
def retrieveAll():
	page = 0
	while True:
		responseObject = api.search( q = 'NHL', fq = {'source':['Reuters','AP', 'The New York Times'], 'news_desk':['sports']}, begin_date = 20111231, page=page)
		articles = responseObject['response']['docs']
		for article in articles:
			print article['headline']['main']
			print "NEWS DESK: ", article['news_desk']
			print "ABSTRACT: ", article['abstract']
			print "SNIPPET: ", article['snippet']
			if article['snippet'] != article['lead_paragraph']:
				print "LEAD PARAGRAPH: ", article['lead_paragraph']
			print ""
		if len(articles) < 10 or page == 0:
			break
		print "NEXT PAGE OF RESULTS:"
		page += 1
#retrieveAll()

def worthKeeping(article):
	if type(article) != type({}):
		return False
	if type(article['headline']) == type({}) and article['headline']['main'] == 'The Weekly Health Quiz':
		return False
	if article['abstract'] is not None:
		return True
	if article['snippet'] is not None:
		return True
	if article['lead_paragraph'] is not None:
		return True
	return False

# If abstract ends in '...', trim that off.
def trimAbstract(abstract):
	if abstract[len(abstract)-3:] == '...':
		abstract = abstract[:len(abstract)-3]
	return abstract

# For convenience
def firstNotInSecond(first, second):
	if second is None:
		return True
	return first not in second

def condenseArticle(article):
	condensed = {}
	condensed['text'] = ""
	if article['abstract'] is not None:
		abstract = trimAbstract(article['abstract'])
		if firstNotInSecond(abstract, article['snippet']) and firstNotInSecond(abstract, article['lead_paragraph']):
			condensed['text'] += abstract
	if article['snippet'] is not None firstNotInSecond(article['snippet'], article['abstract']):
		condensed['text'] += " " + article['snippet']
	if article['lead_paragraph'] is not None:
		condensed['text'] += " " + article['lead_paragraph']
	condensed['headline'] = article['headline']['main']
	condensed['topic'] = article['news_desk']
	condensed['url'] = article['web_url']
	condensed['pub_date'] = article['pub_date']
	return condensed

def retrieveArticlesByNewsDesk(query, newsDesk, begin, end, maxRequests=10):
	t = time()
	articlesToKeep = []
	api = articleAPI('2aeeb020218af0f30993f12ff451d821:10:62878084')
	page = 0
	while True:
		try:
			responseObject = api.search( q = query, fq = {'source':['Reuters','AP', 'The New York Times'], 'news_desk':[newsDesk]}, begin_date = begin, end_date = end, page=page)
		except:
			print "search failed"
			print query, newsDesk, begin, end, maxRequests
			return (articlesToKeep, page+1)
		if 'response' not in responseObject:
			print "No response"
			print query, newsDesk, begin, end, maxRequests
			return (articlesToKeep, page+1)
		articles = responseObject['response']['docs']
		for article in articles:
			if worthKeeping(article):
				condensed = condenseArticle(article)
				#print condensed['pub_date']
				articlesToKeep.append(condensed)
		if len(articles) < 10 or page == maxRequests - 1:
			break
		page += 1
	print ""
	print "Retrieved " + str(len(articlesToKeep)) + " " + newsDesk + " articles."
	print "Made " + str(page+1) + " requests."
	print time() - t
	return (articlesToKeep, page+1)

#retrieveArticlesByNewsDesk('*', 'health')

def todayStr():
	todayDT = datetime.now()
	todayStr = str(todayDT.year)
	todayStr += '%02d' % todayDT.month
	todayStr += '%02d' % todayDT.day
	return todayStr

# Convert from YYYY-MM-DD to YYYYMMMDD format
def convertDateString(date):
	s = date[0:4]
	s += date[5:7]
	s += date[8:10]
	return s

def newCoveredDatesDict(newsDesks):
	coveredDates = {}
	for newsDesk in newsDesks:
		coveredDates[newsDesk] = {}
		coveredDates[newsDesk]['newest'] = None
		coveredDates[newsDesk]['oldest'] = None
	return coveredDates

def getEarliestAndLatestDates(articles):
	earliest = todayStr()
	latest = '20010101'
	for article in articles:
		earliest = min(earliest, article['pub_date'])
		latest = max(latest, article['pub_date'])
	return (convertDateString(earliest), convertDateString(latest))

def saveArticles(articles, newsDesk):
	for article in articles:
		safeHeadline = article['headline'].replace('/','')
		filepath = "./%s/%s_%s.p" % (newsDesk, safeHeadline, article['pub_date'])
		try:
			pickle.dump( article, open( filepath, "wb" ) )
		except:
			continue

def retrieveArticles(maxRequests=50):
	totalRequests = 0
	newsDesks = ['sports','foreign','national','politics','business','technology','science','health','arts','fashion','travel']
	#newsDesks = ['sports','foreign','health']
	try:
		coveredDates = pickle.load(open('dates.p', 'rb'))
	except:
		coveredDates = newCoveredDatesDict(newsDesks)

	for newsDesk in newsDesks:
		# We've got everything for this desk
		if coveredDates[newsDesk]['oldest'] == '20010101' and coveredDates[newsDesk]['newest'] == todayStr():
			continue

		if coveredDates[newsDesk]['newest'] is None:
			print "No covered dates, starting at today..."
			begin = '20010101'
			end = todayStr()
			articles, numRequestsMade = retrieveArticlesByNewsDesk('*', newsDesk, begin, end, maxRequests)
			earliest, latest = getEarliestAndLatestDates(articles)
			print earliest, latest
			coveredDates[newsDesk]['oldest'] = earliest
			coveredDates[newsDesk]['newest'] = latest
			saveArticles(articles, newsDesk)
			totalRequests += numRequestsMade
		else:
			print "Some covered dates, getting most recent thru today..."
			# get the all from newest till today
			articles, numRequestsMade = retrieveArticlesByNewsDesk('*', newsDesk, coveredDates[newsDesk]['newest'], todayStr(), maxRequests)
			print len(articles), " articles retrieved"

			if len(articles) > 0:
				saveArticles(articles, newsDesk)
				earliest, latest = getEarliestAndLatestDates(articles)
				coveredDates[newsDesk]['newest'] = latest

			maxRequests -= numRequestsMade
			totalRequests = numRequestsMade
			
			# if we're not out of requests, start backtracking from oldest to '20010101'
			print "Now working back from oldest covered..."

			if maxRequests > 0:
				articles, numRequestsMade = retrieveArticlesByNewsDesk('*', newsDesk, '20010101', coveredDates[newsDesk]['oldest'], maxRequests)
				print len(articles), " articles retrieved"

				if len(articles) > 0:
					saveArticles(articles, newsDesk)
					earliest, latest = getEarliestAndLatestDates(articles)
					coveredDates[newsDesk]['oldest'] = earliest
				totalRequests = numRequestsMade


	# save our covered dates dict
	pickle.dump(coveredDates, open( "dates.p", "wb" ))


retrieveArticles()
	 





'''
[u'type_of_material', u'blog', u'news_desk', u'lead_paragraph', u'headline', u'abstract', u'print_page', u'word_count', u'_id', u'snippet', u'source', u'web_url', u'multimedia', u'subsection_name', u'keywords', u'byline', u'document_type', u'pub_date', u'section_name']
'''

# NB: setting q='*' appears to give you everything
# News Desks:
# sports
# foreign
# national -- rather fuzzy, though
# politics
# business -- a little fuzzy
# technology
# science
# health -- need to cull 'The Weekly Health Quiz'
# arts
# style -- rather broad, not really fashion...
# fashion -- this actually works
# travel
# entertainment -- from BBC set, not NYTimes