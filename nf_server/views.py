from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from tasks import slowAdd, classify, trainClassifier
from models import Article, NewsFeed, NewsSource

# Create your views here.
def index(request):
	articles = Article.objects.all()
	feeds = NewsFeed.objects.all();
	context = {'articles': articles, 'feeds': feeds}
	return render(request, 'base.html', context)
	#return HttpResponse("index - newsfeed.com/")

def feed(request, feed_id):
	articles = Article.objects.all()
	feed = get_object_or_404(NewsFeed, pk=feed_id)
	name = feed.owner.name
	sources = feed.newsSources.all()
	context = {'sources': sources, 'name': name, 'articles': articles}
	return render(request, 'feed.html', context)

# Create your views here.
def event(request, event_id):
	return HttpResponse("event %s - newsfeed.com/event" % event_id)

def createEvent(request):
	return render(request, 'create_event.html', {})
	#return HttpResponse("So you wanna create an event, eh?")

def newEvent(request):
	return HttpResponse("Making a new event for ya...")

# Create your views here.
def article(request, article_id):
	article = get_object_or_404(Article, pk=article_id)
	return HttpResponse("article %s - newsfeed.com/article" % article_id)

# Create your views here.
def nf_server(request):
	trainClassifier.delay(1,["politics", "alcohol"])
	return HttpResponse("Hi, mom.")