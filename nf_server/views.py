from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from tasks import slowAdd, classify, trainClassifier
from django.core.urlresolvers import reverse
from django.views import generic
from models import Article, NewsFeed, NewsSource, NewsEvent, NewsEventForm, TimelineEntry, Tag
import json
import utils
from django.template.context import RequestContext

def index(request):
	sources = NewsSource.objects.all()
	feeds = NewsFeed.objects.all()
	articles = Article.objects.all()
	context = {'articles': articles, 'sources': sources, 'feeds': feeds, 'request': request,}
	return render(request, 'index.html', context)

def source(request, source_id):
	sources = NewsSource.objects.all()
	feeds = NewsFeed.objects.all()
	source = get_object_or_404(NewsSource, pk=source_id)
	articles = get_list_or_404(Article, newsSource=source_id)
	context = {'source': source, 'articles': articles, 'sources': sources, 'feeds': feeds}
	return render(request, 'source.html', context)

def createSource(request):
	return render(request, 'create_source.html', {})

def newSource(request):
	print "hi"
	responseData = {"name": True, "description": True, "url": True}
	requestData, val = request.POST.items()[0]
	requestData = json.loads(requestData)

	identicalSources = NewsSource.objects.filter(title=requestData["name"])
	if len(identicalSources) > 0:
		responseData["name"] = False

	# do something about the URL later...
	return HttpResponse(json.dumps(responseData), content_type="application/json")

def feed(request, feed_id):
	sources = NewsSource.objects.all()
	feeds = NewsFeed.objects.all()
	feed = get_object_or_404(NewsFeed, pk=feed_id)
	feeds_sources = feed.newsSources.all()
	articles = Article.objects.all()
	context = {'articles': articles, 'feed': feed, 'feeds_sources': feeds_sources, 'sources': sources, 'feeds': feeds}
	return render(request, 'feed.html', context)

# Create your views here.
def event(request, event_id):
	return HttpResponse("event %s - newsfeed.com/event" % event_id)

# Create your views here.
def about(request):
	sources = NewsSource.objects.all()
	feeds = NewsFeed.objects.all()
	articles = Article.objects.all()
	context = {'articles': articles, 'sources': sources, 'feeds': feeds, 'request': request,}
	return render(request, 'about.html', context)
	
def edit (request, feed_id):
	all_sources = NewsSource.objects.all()
	feed = get_object_or_404(NewsFeed, pk=feed_id)
	feeds_sources = feed.newsSources.all()
	context = {'all_sources': all_sources, 'feeds_sources': feeds_sources}
	return render(request, 'edit.html', context)

def createEvent(request, event_id=None):
	context = RequestContext(request, {'user': request.user})
	#print "ID: ", request.user.id, " Name: ", request.user.username
	#print dir(request.user)

	if event_id:
		print "got an id"
		event = get_object_or_404(NewsEvent, pk=event_id)
		form = NewsEventForm(instance=event)
		print event.articles.all()
		form.fields['articles'].queryset = event.articles.all()
		form.fields['editors'].queryset = event.editors.all()

		timelineEntries = []
		for timelineEntry in event.timelineentry_set.all():
			timelineEntries.append([timelineEntry.date.strftime('%b %d, %Y, %I:%M %p'), timelineEntry.text.encode('ascii','ignore'), timelineEntry.id])
			print timelineEntry.date.strftime('%Y-%m-%d %H:%M'), timelineEntry.id
		timelineEntries.sort()

	else:
		print "ain't got no event id"
		event = NewsEvent(owner_id=1)
		event.save()
		print "asdfasdfasdfasdf", event.articles.all()
		form = NewsEventForm(instance=event)
		form.fields['articles'].queryset = event.articles.all()
		form.fields['editors'].queryset = event.editors.all()
		print "the form:", type(form), dir(form)
		print form.is_bound
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

def checkEventTag(request, query):
	print query
	print "checking event tag..."
	matchingEvents = NewsEvent.objects.filter(eventTag=query)
	return HttpResponse(len(matchingEvents))

# Create your views here.
def article(request, article_id):
	article = get_object_or_404(Article, pk=article_id)
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
	return render(request, 'search.html', {})

# Create your views here.
def nf_server(request):
	trainClassifier.delay(1,["politics", "alcohol"])
	return HttpResponse("Hi, mom.")