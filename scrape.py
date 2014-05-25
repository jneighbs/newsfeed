#!/usr/bin/env python

import feedparser
import pprint
import urllib2
import re
import cookielib
from cookielib import CookieJar

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsfeed_site.settings")
from nf_server.models import Article, NewsSource


cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
pp = pprint.PrettyPrinter()

#opener.addHeaders = [('User-agent', 'Mozilla/5.0')]

from django.utils import timezone
def putInDB(entry, sourceName):

	source = NewsSource.objects.get(title=sourceName)
	#convert pub_date
	a = Article(newsSource=source, url=entry.link, pub_date=timezone.now(), summaryText=entry.summary[0:199], title=entry.title)
	a.save()

#scrape Reddit data
def scrapeReddit():

	# grab links
	subredditListUrl = 'http://www.redditlist.com/'
	page_source = opener.open(subredditListUrl).read()

	patFinder = re.compile('<tbody>(.*?)</tbody>', re.DOTALL)
	linkGroups = re.findall(patFinder, page_source)

	mostSubscribedSubreddits = linkGroups[1]
	patFinder = re.compile('href="(.*?)"')
	# top 125 subscribed subreddits
	links = re.findall(patFinder, mostSubscribedSubreddits)


	# parse links/ try to put into db	
	i = 0
	for link in links:
		print "link: " + link
		redditFeed = feedparser.parse(link + '/.rss')
		for entry in redditFeed.entries:
			# pp.pprint(entry.title)
			if len(Article.objects.filter(url=entry.link))==0:
				putInDB(entry, "Reddit")

	# redditFeed = feedparser.parse('http://www.reddit.com/r/coding' + '/.rss')
	# # pp.pprint(redditFeed.entries[0])
	# for entry in redditFeed.entries:
	# 	if len(Article.objects.filter(url=entry.link))==0:
	# 		putInDB(entry, "Reddit")
	


def scrapeNYTimes():
	nyFeed = feedparser.parse("http://rss.nytimes.com/services/xml/rss/nyt/CollegeBasketball.xml")
	print "\n\n"
	print len(nyFeed)
	pp.pprint(nyFeed.entries[0])
	
	# if len(Article.objects.filter(url=nyFeed.entries[0].link))==0:
	# 	putInDB()

def main():

	scrapeReddit()
	# scrapeNYTimes()
	#scrapeEconomist()



main()

