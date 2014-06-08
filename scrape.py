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

# TODO: Might need to surround this in a try catch if it ever reads dynamically
def parseLink(url, source, tagNameFromUrl):
	
	feed = feedparser.parse(url)
	if 'entries' in feed and len(feed.entries) > 0:
		for entry in feed.entries:
			if len(Article.objects.filter(url=entry.link))==0:
				article_id = source+"."+entry.id
				putInDB(entry, source, tagNameFromUrl)


def scrapeImages(entry):

	thumbnail = ""

	if "media_thumbnail" in entry:

		if "url" in entry.media_thumbnail:
			thumbnail = entry.media_thumbnail.url
		elif isinstance(entry.media_thumbnail, list):
			thumbnail = entry.media_thumbnail[0]['url']

	elif "media_content" in entry:
		if "url" in entry.media_content:
			thumbnail = entry.media_content.url
		elif isinstance(entry.media_content, list):
			thumbnail = entry.media_content[0]['url']

	else:

		imgPat = re.compile('<img .*?src="(.*?)"', re.DOTALL)
		thumbnail = re.search(imgPat, entry.summary)
		if thumbnail is None:
			thumbnail = ""
		if thumbnail:	
			thumbnail = thumbnail.group(1)

	# print thumbnail
	return thumbnail

def pullSummary(summaryText):
	replacedText = re.sub('(<(.*?)>|\[link]|&.{1,8};)', "", summaryText)
	return replacedText

def formatTagName(unformattedTagName):
	return unformattedTagName.lower().replace(" ", "").replace("_", "").replace("-", "")

def addTags(article, entry, tagNameFromURL):

	tagArray = []
	if tagNameFromURL:
		tagArray.append(tagNameFromURL)

	if "tags" in entry:
		for tag in entry.tags:
			tagArray.append(tag.term)

	for tagName in tagArray:

		tagName = formatTagName(tagName)
		t, created = Tag.objects.get_or_create(text=tagName)
		if(created): 
			# print "tag created: " + tagName
			t.save()
		t.tagees.add(article)

	return tagArray



def addArticle(entry, sourceName):

	# TODO convert pub_date
	summaryText = pullSummary(entry.summary)
	thumbnail = scrapeImages(entry)
	newsSource = NewsSource.objects.get(title=sourceName)
	article_id = sourceName+"."+entry.id

	article = Article(newsSource=newsSource, url=entry.link, pub_date=timezone.now(), summaryText=summaryText[0:199], thumbnail=thumbnail, title=entry.title, article_id=article_id)
	article.save()

	print "New entry! : " + article_id

	return article



def putInDB(entry, sourceName, tagNameFromURL):

	article = addArticle(entry, sourceName)
	tags = addTags(article, entry, tagNameFromURL)



#scrape Reddit data
def scrapeReddit():

	print "##########\n# Reddit #\n##########"
	sourceName = "Reddit"
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
		# print "link: " + link
		redditFeed = feedparser.parse(link + '/.rss')

		tagFinder = re.compile('http://reddit.com/r/(.*)/')
		tag = re.match(tagFinder, link)
		tagNameFromURL = formatTagName(tag.group(1))

		for entry in redditFeed.entries:
			# pp.pprint(entry.title)

			article_id = sourceName+"."+entry.id
			if len(Article.objects.filter(article_id=article_id))==0:
				putInDB(entry, sourceName, tagNameFromURL)	


def scrapeNYTimes():

	# http://rss.nytimes.com/services/xml/rss/nyt/World.xml
	print "###########\n# NYTimes #\n###########"
	sourceName = "The New York Times"
	# grab links
	nyTimesListUrl = 'http://www.nytimes.com/services/xml/rss/index.html'
	page_source = opener.open(nyTimesListUrl).read()

	linkFinder = re.compile('href="((http://www.nytimes.com/services/xml/rss/nyt/|http://feeds.nytimes.com/nyt/rss/)(.*?))"', re.DOTALL)
	linkGroups = re.findall(linkFinder, page_source)


	for link in linkGroups:
		tag = link[2]
		link = link[0]
		if(link[-5:] != ".opml"):
			# print "link: " + link
			if tag[-4:]==".xml":
				tag = tag[0:-4]
			
			nyTimesFeed = feedparser.parse(link)
			tagNameFromURL = formatTagName(tag)

			for entry in nyTimesFeed.entries:

				# print "entry.link: " + entry.link
				article_id = sourceName + "." + entry.id
				
				if len(Article.objects.filter(article_id=article_id))==0:
					putInDB(entry, sourceName, tagNameFromURL)


def scrapeTwitter():

	twitterURL = "http://api.twitter.com/1.1/search/tweets.json?q=%23freebandnames&since_id=24012619984051000&max_id=250126199840518145&result_type=mixed&count=4"
	req = urllib2.Request(twitterURL)
	res = urllib2.urlopen(req)
	print res.read()


def main():

	# readFromFile()

	# scrapeTwitter()

	print "###############\n# Tech Crunch #\n###############"
	parseLink("http://feeds.feedburner.com/TechCrunch/", "Tech Crunch", "")

	print "#################\n# Time Magazine #\n#################"
	parseLink("http://time.com/newsfeed/feed/", "Time Magazine", "all")
	
	print "################\n# ScienceDaily #\n################"
	parseLink("http://feeds.sciencedaily.com/sciencedaily?format=xml", "ScienceDaily", "all")
	parseLink("http://feeds.sciencedaily.com/sciencedaily/top_news?format=xml", "ScienceDaily", "topnews")
	parseLink("http://feeds.sciencedaily.com/sciencedaily/most_popular?format=xml", "ScienceDaily", "mostpopular")

	scrapeNYTimes()
	scrapeReddit()

main()

