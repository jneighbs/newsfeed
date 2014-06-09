import feedparser
import urllib2
import cookielib
from cookielib import CookieJar
import operator
from django.db.models import Q

cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))


from nf_server.models import Article, NewsFeed, NewsSource, NewsEvent, Tag, User, Rating

# Given a set of models and a query, returns all the instances
# of all the models that contain that query in their title.
# 
# returned object is a dictionary with models as keys and dictionaries
# with model id as keys and titles as values.
def findExactMatches(models, query):

	results = {}

	if 'articles' in models:
		results['articles'] = Article.objects.filter(title__contains=query)
	if 'feeds' in models:
		results['feeds'] = NewsFeed.objects.filter(title__contains=query)
	if 'sources' in models:
		results['sources'] = NewsSource.objects.filter(title__contains=query)
	if 'events' in models:
		results['events'] = NewsEvent.objects.filter(title__contains=query)
	if 'tags' in models:
		results['tags'] = Tag.objects.filter(text__contains=query)
	if 'users' in models:
		results['users'] = User.objects.filter(name__contains=query)
	
	
	responseData = {}

	for model in results:
		responseData[model] = {}
		for result in results[model]:
			responseData[model][result.id] = result.allText()
			if len(responseData[model]) > 14:
				break
		
	return responseData

# Given a list of models, a set of words, and a threshold, finds all instances
# of all the given models that have >= threshold % of query words in
# their .allText()
#
# Returns a response object of the same format as the findExactMatches methd
def findPartialMatches(models, queryWords, responseData, threshold):
	for model in models:

		if model not in responseData:
			responseData[model] = {}

		if model == 'articles':
			#candidates = Article.objects.order_by('pub_date').all()
			candidates = Article.objects.filter(reduce(operator.and_, (Q(summaryText__contains=x) for x in queryWords)))
			candidates = candidates & Article.objects.filter(reduce(operator.and_, (Q(title__contains=x) for x in queryWords)))
		elif model == 'feeds':
			candidates = NewsFeed.objects.all()
		elif model == 'sources':
			candidates = NewsSource.objects.all()
		elif model == 'events':
			candidates = NewsEvent.objects.all()
		elif model == 'tags':
			candidates = Tag.objects.all()
		elif model == 'users':
			candidates = User.objects.all()

		for candidate in candidates:
			if candidate.id in responseData[model]:
				continue
			#print candidate.allText()

			queryWordCount = 0.0
			for queryWord in queryWords:
				if queryWord in candidate.allText().lower():
					queryWordCount += 1.0

			if queryWordCount / len(queryWords) >= threshold:
				responseData[model][candidate.id] = candidate.title
			
			if len(responseData[model]) > 14:
				break
	return responseData

def tagSearch(models, query):
	#print models
	#print query

	responseData = {}

	matchingTags = Tag.objects.filter(text__contains=query)
	#print "found matching tags", matchingTags
	for model in models:
		#print "finding ", model
		responseData[model] = {}

		if model not in responseData:
			responseData[model] = {}

		if model == 'articles':
			#candidates = Article.objects.order_by('pub_date').all()
			try:
				matches = Article.objects.filter(reduce(operator.and_, (Q(tag=x) for x in matchingTags)))
			except TypeError:
				matches = []
		elif model == 'feeds':
			try:
				matches = NewsFeed.objects.filter(reduce(operator.and_, (Q(tag=x) for x in matchingTags)))
			except TypeError:
				matches = []
		elif model == 'sources':
			try:
				matches = NewsSource.objects.filter(reduce(operator.and_, (Q(tag=x) for x in matchingTags)))
			except TypeError:
				matches = []
		elif model == 'events':
			try:
				matches = NewsEvent.objects.filter(reduce(operator.and_, (Q(tag=x) for x in matchingTags)))
			except TypeError:
				matches = []
		else:
			matches = []

		for match in matches:
			responseData[model][match.id] = match.title

		# for candidate in candidates:

		# 	for tag in candidate.tag_set.all():
		# 		if query in tag.text.lower():
		# 			responseData[model][candidate.id] = candidate.title

		if len(responseData[model]) > 14:
			break;
	return responseData

def urlIsBroken(url):

	feed = feedparser.parse(url)
	print feed
	return not ('entries' in feed and len(feed.entries) > 0)


def getRating(objectId, user):
	if user.id and not user.is_anonymous:
		rating = Rating.objects.filter(ratee_id=objectId, rater_id=user.id)
		if len(rating) > 0:
			ratingValue = rating[0].rating
		else:
			ratingValue = 0
	else:
		ratingValue = 0

	return ratingValue

def canEdit(eventId, user):
	if (not user) or user.is_anonymous():
		return False

	event = NewsEvent.objects.get(id=eventId)
	if user.id != event.owner_id and len(event.editors.filter(id=user.id)) == 0:
		return False

	return True

def canEditFeed(feedId, user):
	if (not user) or user.is_anonymous():
		return False

	feed = NewsFeed.objects.get(id=feedId)
	if user.id != feed.owner_id:
		return False

	return True


