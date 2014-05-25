from nf_server.models import Article, NewsFeed, NewsSource, NewsEvent, Tag

# Given a set of models and a query, returns all the instances
# of all the models that contain that query in their title.
# 
# returned object is a dictionary with models as keys and dictionaries
# with model id as keys and titles as values.
def findExactMatches(models, query):
	print models

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
	
	print "survived result creation...", results
	
	responseData = {}
	
	for model in results:
		responseData[model] = {}
		for result in results[model]:
			if model == 'tags':
				responseData[model][result.id] = result.text
			else:
				responseData[model][result.id] = result.title
	
	print "exact match response data", responseData
	
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
			candidates = Article.objects.order_by('pub_date').all()
		elif model == 'feeds':
			candidates = NewsFeed.objects.all()
		elif model == 'sources':
			candidates = NewsSource.objects.all()
		elif model == 'events':
			candidates = NewsEvent.objects.all()
		elif model == 'tags':
			candidates = Tag.objects.all()

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
	return responseData