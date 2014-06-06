#!/usr/bin/env python

import feedparser
import pprint
import urllib2
import re
import cookielib
from cookielib import CookieJar
from django.utils import timezone

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsfeed_site.settings")
from nf_server.models import Article, NewsSource, Tag


cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
pp = pprint.PrettyPrinter()

#opener.addHeaders = [('User-agent', 'Mozilla/5.0')]


# TODO: Take in entry instead of summary text. Parse something before summary text, if no img exists there, then parse summary text
def scrapeImages(entry):

	thumbnail = ""
	if "media_content" in entry:
		if "url" in entry.media_content:
			thumbnail = entry.media_content.url

	else:

		imgPat = re.compile('<img .*?src="(.*?)"', re.DOTALL)
		thumbnail = re.search(imgPat, entry.summary)
		if thumbnail is None:
			thumbnail = ""
		if thumbnail:	
			thumbnail = thumbnail.group(1)
	return thumbnail

def pullSummary(summaryText):
	pPat = re.compile('<p>(.*?)</p>', re.DOTALL)
	pGroups = re.findall(pPat, summaryText)

	text = ""
	for p in pGroups:
		print p
		text = text + p
	print text

	return text

def formatTagName(unformattedTagName):
	return unformattedTagName.lower().replace(" ", "").replace("_", "").replace("-", "")

def addTags(article, entry, tagNameFromURL):

	tagArray = [tagNameFromURL]

	if "tags" in entry:
		for tag in entry.tags:
			tagArray.append(tag.term)

	for tagName in tagArray:

		tagName = formatTagName(tagName)
		t, created = Tag.objects.get_or_create(text=tagName)
		if(created): 
			print "tag created: " + tagName
			t.save()
		t.tagees.add(article)

	return tagArray



def addArticle(entry, sourceName):

	# TODO convert pub_date
	# TODO add summaries
	# summaryText = pullSummary(entry)
	
	thumbnail = scrapeImages(entry)
	newsSource = NewsSource.objects.get(title=sourceName)

	article = Article(newsSource=newsSource, url=entry.link, pub_date=timezone.now(), summaryText="", thumbnail=thumbnail, title=entry.title)
	article.save()

	return article



def putInDB(entry, sourceName, tagNameFromURL):

	article = addArticle(entry, sourceName)
	tags = addTags(article, entry, tagNameFromURL)



#scrape Reddit data
def scrapeReddit():

	print "##########\n# Reddit #\n##########"

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

	for link in links:
		print "link: " + link
		redditFeed = feedparser.parse(link + '/.rss')

		tagFinder = re.compile('http://reddit.com/r/(.*)/')
		tag = re.match(tagFinder, link)
		tagNameFromURL = formatTagName(tag.group(1))

		for entry in redditFeed.entries:
			# pp.pprint(entry.title)
			if len(Article.objects.filter(url=entry.link))==0:
				putInDB(entry, "Reddit", tagNameFromURL)	


def scrapeNYTimes():

	# http://rss.nytimes.com/services/xml/rss/nyt/World.xml
	print "###########\n# NYTimes #\n###########"
	
	# grab links
	nyTimesListUrl = 'http://www.nytimes.com/services/xml/rss/index.html'
	page_source = opener.open(nyTimesListUrl).read()

	linkFinder = re.compile('href="((http://www.nytimes.com/services/xml/rss/nyt/|http://feeds.nytimes.com/nyt/rss/)(.*?))"', re.DOTALL)
	linkGroups = re.findall(linkFinder, page_source)

	for link in linkGroups:
		tag = link[2]
		link = link[0]
		if(link[-5:] != ".opml"):
			print "link: " + link
			if tag[-4:]==".xml":
				tag = tag[0:-4]
			
			nyTimesFeed = feedparser.parse(link)
			tagNameFromURL = formatTagName(tag)

			for entry in nyTimesFeed.entries:

				if len(Article.objects.filter(url=entry.link))==0:
					putInDB(entry, "NYTimes", tagNameFromURL)


def main():

	# readFromFile()
	scrapeReddit()
	scrapeNYTimes()
	# scrapeEconomist()



main()

