#!/usr/bin/env python

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from django.utils import timezone
import json

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsfeed_site.settings")
from nf_server.models import Tweet, NewsSource

ckey = "zxv5PuVTMmkz6RsgfGNmXp0mW"
csecret = "tyzhrTZVpCMcNWGs2kXSn4o8InPbAJkI9xm176TyMStpfNhc8X"
atoken = "1216830606-eXqhJtOp3Sv0alAmEzMmCkyNP9VCvcCLo2XUgEq"
asecret = "Gs7K8vqWiwrHSAiXVnd24schGo3pdB5gxPbXGoVq2Glas"

class listener(StreamListener):

	def on_data(self, stringJSON):

		print "new tweet"

		data = json.loads(stringJSON)
		summaryText = data["text"]
		thumbnail = ""
		sourceName = "Twitter"
		newsSource = NewsSource.objects.get(title=sourceName)
		article_id = sourceName+"." + data["id_str"]

		tweet = Tweet(newsSource=newsSource, pub_date=timezone.now(), summaryText=summaryText[0:199], title="", article_id=article_id)
		tweet.save()

		return True

	def on_error(self, status):
		print status

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
twitterStream.filter(track=["cars"])