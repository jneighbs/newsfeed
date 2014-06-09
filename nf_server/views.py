from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from tasks import slowAdd, classify, trainClassifier
from django.core.urlresolvers import reverse
from django.views import generic
from models import Article, NewsFeed, NewsSource, NewsEvent, NewsEventForm, TimelineEntry, Tag, Rating, User
import json
import utils
import re
from django.template.context import RequestContext
from itertools import chain
from operator import attrgetter
import datetime

def index(request):
	sources = NewsSource.objects.all()
	feeds = NewsFeed.objects.all()
	articles = Article.objects.all()[:20]
	topEvents = NewsEvent.objects.all().order_by("score")[:5]
	context = {'articles': articles, 'sources': sources, 'feeds': feeds, 'request': request, 'topEvents': topEvents}
	return render(request, 'index.html', context)

def source(request, source_id):
	sources = NewsSource.objects.all()
	feeds = NewsFeed.objects.all()
	source = get_object_or_404(NewsSource, pk=source_id)
	source.viewCount += 1
	source.score += 1
	source.save()
	rating = utils.getRating(source_id, request.user)
	topEvents = NewsEvent.objects.all().order_by("score")[:5]
	articles = Article.objects.filter(newsSource=source_id)[:20]
	context = {'source': source, 'articles': articles, 'sources': sources, 'feeds': feeds, 'rating': rating, 'topEvents': topEvents,}
	return render(request, 'source.html', context)

def createSource(request):
	return render(request, 'create_source.html', {})

def validateSource(request):
	responseData = {"name": True, "description": True, "url": True}

	requestData, val = request.POST.items()[0]
	requestData = json.loads(requestData)

	if len(requestData["name"]) == 0:
		responseData["name"] = ""
	else:
		identicalSources = NewsSource.objects.filter(title=requestData["name"])
		if len(identicalSources) > 0:
			responseData["name"] = "That name is already taken."
	
	if len(requestData["url"]) == 0:
		responseData["url"] = ""
	elif utils.urlIsBroken(requestData["url"]):
		responseData["url"] = "That URL appears to be broken."
	else:
		identicalUrls = NewsSource.objects.filter(url=requestData["url"])
		if len(identicalUrls) > 0:
			responseData["url"] = "That source already exists."
	
	return HttpResponse(json.dumps(responseData), content_type="application/json")

def newSource(request):
	source = NewsSource()
	source.title = request.POST["name"]
	source.description = request.POST["description"]
	source.url = request.POST["url"]
	source.save()
	return HttpResponseRedirect("/source/" + str(source.id))

def feed(request, feed_id):
	sources = NewsSource.objects.all()
	feeds = NewsFeed.objects.all()
	feed = get_object_or_404(NewsFeed, pk=feed_id)
	feed.viewCount += 1
	feed.score += 1
	feed.save()
	feed_sources = feed.newsSources.all()

	sourceIds = [source.id for source in feed_sources]
	articles = Article.objects.filter(newsSource_id__in=sourceIds).order_by("pub_date").reverse()[:20]

	ratingValue = utils.getRating(feed_id, request.user)
	topEvents = NewsEvent.objects.all().order_by("score")[:5]

	context = {'articles': articles, 'feed': feed, 'feed_sources': feed_sources, 'sources': sources, 'feeds': feeds, 'rating': ratingValue, 'topEvents': topEvents,}
	return render(request, 'feed.html', context)

def saveRating(request, feed_id):
	#print "saving rating"

	if request.POST["userID"] == "None":
		userID = -1
	else:
		userID = request.POST["userID"]

	if request.POST["rating"] >= 1:
		#print request.POST["rating"]
		ratings = Rating.objects.filter(ratee_id=feed_id, rater_id=userID)
		feed = NewsFeed.objects.get(id=feed_id)
		if len(ratings) > 0:
			#print "getting old rating"
			rating = ratings[0]
			
			feed.score -= rating.rating
			
		else:
			#print "creating new rating"
			rating = Rating()

		rating.rating = request.POST["rating"]
		rating.rater_id = userID
		rating.ratee_id = feed_id
		feed.score += request.POST["rating"]

		#print "done setting fields"

		if userID != -1:
			rating.save()
		#else:
		#	print "just kidding"

		#print rating
	return HttpResponse("woohoo")



# Create your views here.
def event(request, event_id):
	sources = NewsSource.objects.all()
	feeds = NewsFeed.objects.all()
	articles = Article.objects.all()[:20]
	topEvents = NewsEvent.objects.all().order_by("score")[:5]
	event = NewsEvent.objects.get(id=event_id)
	event.viewCount += 1
	event.score += 1
	event.save()
	rating = utils.getRating(event_id, request.user)
	canEdit = utils.canEdit(event_id, request.user)
	topEvents = NewsEvent.objects.all().order_by("score")[:5]
	context = {'articles': articles, 'sources': sources, 'feeds': feeds, 'event': event, 'rating': rating, 'topEvents': topEvents, 'canEdit': canEdit,}
	return render(request, 'event.html', context)

	
def editFeed (request, feed_id):
	all_sources = NewsSource.objects.all()
	feed = get_object_or_404(NewsFeed, pk=feed_id)
	feeds_sources = feed.newsSources.all()
	context = {'all_sources': all_sources, 'feeds_sources': feeds_sources, 'feed': feed}
	return render(request, 'edit_feed.html', context)

def saveFeed(request):
	# start doing actual work
	f = NewsFeed.objects.get(pk=request.POST['pk'])
	print f.id

	f.newsSources.clear()
	if 'checkboxes' in request.POST:
		for newsSourceId in request.POST.getlist('checkboxes'):
			f.newsSources.add(newsSourceId)

	if 'title' in request.POST:
		f.title = request.POST['title']

	f.save()
	return HttpResponseRedirect("/feed/" + request.POST['pk'])

def createFeed(request, feed_id=None):
	context = RequestContext(request, {'user': request.user})
	print "ID: ", request.user.id, " Name: ", request.user.username, request.user.is_anonymous()
	#print dir(request.user)

	if (not request.user) or request.user.is_anonymous():
		#return HttpResponseRedirect("/event/" + str(event_id))
		print "bad user! not logged in! not your event!"

	if feed_id:
		print "got an id"
		feed = get_object_or_404(NewsFeed, pk=feed_id)
		
		if request.user.id != feed.owner_id:
			print "not your event, kiddo"
			#return HttpResponseRedirect("/event/" + str(event_id))
	else:

		if (not request.user) or request.user.is_anonymous():
			#return HttpResponseRedirect("/event/" + str(event_id))
			print "bad user! not logged in! not your event!"

		print "ain't got no event id"
		feed = NewsFeed(owner_id=request.user.id)
		feed.save()
	#return HttpResponse("So you wanna create an event, eh?")
	all_sources = NewsSource.objects.all()
	return render(request, 'create_feed.html', {'all_sources': all_sources, 'feed':feed })

def newFeed(request):
	# start doing actual work
	f = NewsFeed.objects.get(pk=request.POST['pk'])
	print f.id

	f.newsSources.clear()
	if 'checkboxes' in request.POST:
		for newsSourceId in request.POST.getlist('checkboxes'):
			f.newsSources.add(newsSourceId)

	if 'title' in request.POST:
		f.title = request.POST['title']

	if 'description' in request.POST:
		f.description = request.POST['description']

	f.save()
	return HttpResponseRedirect("/feed/" + request.POST['pk'])

def createEvent(request, event_id=None):
	context = RequestContext(request, {'user': request.user})
	print "ID: ", request.user.id, " Name: ", request.user.username, request.user.is_anonymous()
	#print dir(request.user)

	if (not request.user) or request.user.is_anonymous():
		#return HttpResponseRedirect("/event/" + str(event_id))
		print "bad user! not logged in! not your event!"

	if event_id:
		print "got an id"
		event = get_object_or_404(NewsEvent, pk=event_id)
		
		if request.user.id != event.owner_id and len(event.editors.filter(id=request.user.id)) == 0:
			print "not your event, kiddo"
			#return HttpResponseRedirect("/event/" + str(event_id))

		form = NewsEventForm(instance=event)
		form.fields['articles'].queryset = event.articles.all()
		form.fields['editors'].queryset = event.editors.all()

		timelineEntries = []
		for timelineEntry in event.timelineentry_set.all():
			timelineEntries.append([timelineEntry.date.strftime('%b %d, %Y, %I:%M %p'), timelineEntry.text.encode('ascii','ignore'), timelineEntry.id])
			print timelineEntry.date.strftime('%Y-%m-%d %H:%M'), timelineEntry.id
		timelineEntries.sort()

	else:

		if (not request.user) or request.user.is_anonymous():
			#return HttpResponseRedirect("/event/" + str(event_id))
			print "bad user! not logged in! not your event!"

		print "ain't got no event id"
		event = NewsEvent(owner_id=request.user.id)
		event.save()
		form = NewsEventForm(instance=event)
		form.fields['articles'].queryset = event.articles.all()
		form.fields['editors'].queryset = event.editors.all()
		timelineEntries = []
	

	return render(request, 'create_event.html', {'form': form, 'event': event, 'timelineEntries': timelineEntries})
	#return HttpResponse("So you wanna create an event, eh?")

def newEvent(request):
	# some printout crap
	for param, val in request.POST.items():
		print param, val
	print "articles:", request.POST.getlist('articles')
	
	# start doing actual work
	e = NewsEvent.objects.get(pk=request.POST['pk'])
	print e.id

	e.articles.clear()
	if 'articles' in request.POST:
		for articleId in request.POST.getlist('articles'):
			e.articles.add(articleId)

	if 'title' in request.POST:
		e.title = request.POST['title']

	if 'eventTag' in request.POST:
		e.eventTag = request.POST['eventTag']

	# handle TimelineEntries
	if 'timelineEntry_add' in request.POST:
		for timelineEntry in request.POST.getlist('timelineEntry_add'):
			newTLEntry = TimelineEntry()
			newTLEntry.text = timelineEntry
			newTLEntry.event_id = request.POST['pk']
			newTLEntry.save()
	for param, val in request.POST.items():
		index = param.find('timelineEntry_')
		if index > -1 and param != 'timelineEntry_add':
			tlEntryId = param[index+len('timelineEntry_'):]
			tlEntry = TimelineEntry.objects.get(pk=tlEntryId)
			tlEntry.text = val
			tlEntry.save()

	# Editors
	e.editors.clear()
	if 'editors' in request.POST:
		print "handling editors..."
		for editorId in request.POST.getlist('editors'):
			print editorId
			e.editors.add(editorId)


	# tags
	e.tag_set.clear()
	if 'tags' in request.POST:
		
		for tagVal in request.POST.getlist('tags'):
			try:
				tagVal = int(tagVal)
				e.tag_set.add(tagVal)
			except ValueError:
				newTag = Tag()
				newTag.text = tagVal
				newTag.save()
				e.tag_set.add(newTag.id)

	e.save()

	return HttpResponseRedirect("/edit_event/" + request.POST['pk'])

def validateEvent(request):
	print "hi"
	requestData, val = request.POST.items()[0]
	requestData = json.loads(requestData)
	print requestData, type(requestData)
	
	responseData = {}
	for name in requestData:
		value = requestData[name]
		if name == "title":
			if len(value) == 0:
				responseData[name] = "An event needs a name."
			else:
				responseData[name] = True
		elif name == "eventTag":
			if len(value) == 0:
				responseData[name] = "An event needs an event tag."
			elif " " in value:
				responseData[name] = "No spaces allowed in event tags."
			elif re.match('^[\w-]+$', value) is None:
				responseData[name] = "Only letters and numbers in event tags."
			else:
				responseData[name] = True
		else:
			responseData[name] = True
	print responseData

	return HttpResponse(json.dumps(responseData), content_type="application/json")

def checkEventTag(request, query):
	print query
	print "checking event tag..."
	matchingEvents = NewsEvent.objects.filter(eventTag=query)
	return HttpResponse(len(matchingEvents))

# Create your views here.
def article(request, article_id):
	article = get_object_or_404(Article, pk=article_id)
	article.viewCount += 1
	article.score += 1
	article.save()
	return HttpResponseRedirect(article.url)
	return HttpResponse("article %s - newsfeed.com/article" % article_id)

def fireSearch(request, query):
	validModels = ['articles', 'feeds', 'sources', 'events', 'tags', 'users']
	models = [model for model in request.GET.get('models', '').split() if model in validModels]	

	query = query.lower()

	responseData = utils.findExactMatches(models, query)

	queryWords = set(query.split())

	if len(queryWords) == 0:
		return HttpResponse(json.dumps(responseData), content_type="application/json")

	responseData = utils.findPartialMatches(models, queryWords, responseData, 0.5)

	return HttpResponse(json.dumps(responseData), content_type="application/json")

def fireTagSearch(request, query):
	print "searching over tags..."
	validModels = ['articles', 'feeds', 'sources', 'events', 'tags', 'users']
	models = [model for model in request.GET.get('models', '').split() if model in validModels]	

	query = query.lower()

	responseData = utils.tagSearch(models, query)
	return HttpResponse(json.dumps(responseData), content_type="application/json")

def search(request):
	sources = NewsSource.objects.all()
	feeds = NewsFeed.objects.all()
	articles = Article.objects.all()[:20]
	topEvents = NewsEvent.objects.all().order_by("score")[:5]
	context = {'articles': articles, 'sources': sources, 'feeds': feeds, 'request': request, 'topEvents': topEvents}
	return render(request, 'search.html', context)

def loadMore(request):
	for param, val in request.GET.items():
		print param, val
	chunksLoaded = int(request.GET['chunksLoaded'])

	if request.GET['model'] == "feed":
		obj = NewsFeed.objects.get(id=request.GET["id"])
		print "got feed"
		sourceIds = [source.id for source in obj.newsSources.all()]
		print "got list of sources"
		results = Article.objects.filter(newsSource_id__in=sourceIds).order_by("pub_date").reverse()
	elif request.GET["model"] == "source":
		obj = NewsSource.objects.get(id=request.GET["id"])
		results = obj.article_set.all().order_by("pub_date").reverse()
	print "so far so good"
	results = results[chunksLoaded*20:(chunksLoaded+1)*20]
	print "sliced fine"
	responseData = []
	for result in results:
		responseObj = {
		"id": result.id,
		"title": result.title,
		"url": result.url,
		"pubDate": result.pub_date.strftime('%b %d, %Y, %I:%M %p'),
		"sourceTitle": result.newsSource.title,
		"summaryText": result.summaryText
		}
		responseData.append(responseObj)
	print "packed up response data"
	print responseData
	return HttpResponse(json.dumps(responseData), content_type="application/json")

# Create your views here.
def nf_server(request):
	trainClassifier.delay(1,["politics", "alcohol"])
	return HttpResponse("Hi, mom.")