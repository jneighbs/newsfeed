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
	addSource("Reddit", "", "United States")

	#add NYTimes NewsSource	
	addSource("The New York Times", "", "United States")

	#add the Economist NewsSource	
	addSource("Tech Crunch", "", "United States")

	#add the ScienceDaily NewsSource	
	addSource("ScienceDaily", "", "United States")

	#add the Time Magazine NewsSource	
	addSource("Time Magazine", "", "United States")

main()