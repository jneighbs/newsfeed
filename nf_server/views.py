from django.shortcuts import render
from django.http import HttpResponse
from tasks import slowAdd, classify, trainClassifier

# Create your views here.
def index(request):
	trainClassifier.delay(1,["politics", "alcohol"])
	return HttpResponse("Hi, mom.")