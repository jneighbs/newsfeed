#!/usr/bin/env python

import sys
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from django.utils import timezone
import json
import time

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsfeed_site.settings")
from nf_server.models import Tweet

ckey = "zxv5PuVTMmkz6RsgfGNmXp0mW"
csecret = "tyzhrTZVpCMcNWGs2kXSn4o8InPbAJkI9xm176TyMStpfNhc8X"
atoken = "1216830606-eXqhJtOp3Sv0alAmEzMmCkyNP9VCvcCLo2XUgEq"
asecret = "Gs7K8vqWiwrHSAiXVnd24schGo3pdB5gxPbXGoVq2Glas"



class listener(StreamListener):

	searchTerm = "yuyu"

	def on_data(self, stringJSON):

		try:
			print "new tweet"
			searchTerm = listener.searchTerm

			data = json.loads(stringJSON)
			text = data["text"]
			tweet_id =data["id_str"]

			tweet = Tweet(searchTerm=searchTerm, pub_date=timezone.now(), text=text, title="", tweet_id=tweet_id)
			tweet.save()

			return False
		except BaseException, e:
			print "failed on_data" + str(e)
			time.sleep(10)

	def on_error(self, status):
		print status + "exiting.."
		return False

	def on_timeout(self):
		return False

	def on_disconnect(self, notice):
		return False



def stream(givenTerm):
	# i=0
	# for arg in sys.argv:
	# 	if i == 1:
	# 		searchTerm = arg
	# 	i = i+1

	print "searchTerm: "+givenTerm
	listener.searchTerm = str(givenTerm)

	try:
		auth = OAuthHandler(ckey, csecret)
		auth.set_access_token(atoken, asecret)
		twitterStream = Stream(auth, listener())
		twitterStream.filter(track=[givenTerm])
	except BaseException, e:
		print "too many connections to twitter! Chill out a sec!" + str(e)
		time.sleep(5)



# main()