#!/usr/bin/env python

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from django.utils import timezone
import json

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsfeed_site.settings")
from nf_server.models import Tweet

ckey = "zxv5PuVTMmkz6RsgfGNmXp0mW"
csecret = "tyzhrTZVpCMcNWGs2kXSn4o8InPbAJkI9xm176TyMStpfNhc8X"
atoken = "1216830606-eXqhJtOp3Sv0alAmEzMmCkyNP9VCvcCLo2XUgEq"
asecret = "Gs7K8vqWiwrHSAiXVnd24schGo3pdB5gxPbXGoVq2Glas"

class listener(StreamListener):

	def on_data(self, stringJSON):

		print "new tweet"

		data = json.loads(stringJSON)
		text = data["text"]
		thumbnail = ""
		tweet_id =data["id_str"]

		tweet = Tweet(pub_date=timezone.now(), text=text, title="", tweet_id=tweet_id)
		tweet.save()

		return True

	def on_error(self, status):
		print status

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
twitterStream.filter(track=["cars"])