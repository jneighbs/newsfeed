from django.shortcuts import render
from django.http import HttpResponse
from tasks import slowAdd, classify, trainClassifier

# Create your views here.
def index(request):
	return HttpResponse("index - newsfeed.com/")

# Create your views here.
def event(request):
	return HttpResponse("event - newsfeed.com/event")

# Create your views here.
def article(request):
	return HttpResponse("article - newsfeed.com/article")

# Create your views here.
def nf_server(request):
	trainClassifier.delay(1,["politics", "alcohol"])
	return HttpResponse("Hi, mom.")