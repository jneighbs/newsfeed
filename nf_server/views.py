from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from tasks import slowAdd, classify, trainClassifier
from django.core.urlresolvers import reverse
from django.views import generic
from models import Article, NewsFeed, NewsSource, NewsEvent, NewsEventForm
import json
import utils

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
	if event_id:
		print "got an id"
		event = get_object_or_404(NewsEvent, pk=event_id)
		form = NewsEventForm(instance=event)

	else:
		print "ain't got no event id"
		event = NewsEvent(owner_id=1)
		event.save()
		form = NewsEventForm()
	

	return render(request, 'create_event.html', {'form': form, 'event': event})
	#return HttpResponse("So you wanna create an event, eh?")

def newEvent(request):
	return HttpResponse("Making a new event for ya...")

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
	validModels = ['articles', 'feeds', 'sources', 'events']
	models = [model for model in request.GET.get('models', '').split() if model in validModels]	

	query = query.lower()

	responseData = utils.findExactMatches(models, query)

	queryWords = set(query.split())

	if len(queryWords) == 0:
		return HttpResponse(json.dumps(responseData), content_type="application/json")

	responseData = utils.findPartialMatches(models, queryWords, responseData, 0.5)

	return HttpResponse(json.dumps(responseData), content_type="application/json")

def search(request):
	return render(request, 'search.html', {})

# Create your views here.
def nf_server(request):
	trainClassifier.delay(1,["politics", "alcohol"])
	return HttpResponse("Hi, mom.")