from django.shortcuts import render
from django.http import HttpResponse
from tasks import slowAdd

# Create your views here.
def index(request):
	slowAdd.delay(2,2)
	return HttpResponse("Hi, mom.")