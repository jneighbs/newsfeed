#!/usr/bin/env python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsfeed_site.settings")
from nf_server.models import NewsSource

def addSource(title, description, country):
	if len(NewsSource.objects.filter(title=title))==0:
		print "adding NewsSource: " + title
		source = NewsSource(title=title, country=country, description=description)
		source.save()


def main():

	#add Reddit NewsSource	
	addSource("Reddit", "Front page of the internet, bitchez", "United States")

	#add NYTimes NewsSource	
	addSource("The New York Times", "New York Times, blah blah", "United States")

	#add the Economist NewsSource	
	addSource("The Economist", "The economy and money and stuff", "United States")

main()