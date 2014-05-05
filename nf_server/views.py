from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from tasks import slowAdd, classify, trainClassifier
from nf_server.models import NewsEvent, Article, NewsEventForm

# Create your views here.
def index(request):
	return HttpResponse("index - newsfeed.com/")

# Create your views here.
def event(request, event_id):
	return HttpResponse("event %s - newsfeed.com/event" % event_id)

def createEvent(request, event_id=None):

	if event_id:
		print "got an id"
		event = get_object_or_404(NewsEvent, pk=event_id)
		form = NewsEventForm(instance=event)

	else:
		print "ain't got no event id"
		form = NewsEventForm()
	

	return render(request, 'create_event.html', {'form': form})
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