from django.db import models

# Create your models here.

# An abstract object that has a title and has many comments and tags and ratings
class NewsObject(models.Model):
	title = models.CharField(max_length=200)

	def __unicode__(self):
		return self.title


class NewsSource(NewsObject):
	country = models.CharField(max_length=30)

class NewsFeed(NewsObject):
	feed_title = models.CharField(max_length=60)

	# has many newsSources
	newsSources = models.ManyToManyField(NewsSource)
	# belongs to a user
	owner = models.ForeignKey('User', related_name='ownedNewsFeeds')
	
	# user_set
	# tag_set

	# DO LATER
	# has many topic filters
	# has a user filter?

class User(models.Model):
	# CHANGE THESE TWO LATER
	# first name / last name
	name = models.CharField(max_length=60)
	# password
	password = models.CharField(max_length=200)

	# follows many news feeds
	followedNewsFeeds = models.ManyToManyField(NewsFeed, related_name='followers')

	def __unicode__(self):
		return self.name

class Article(NewsObject):
	newsSource = models.ForeignKey(NewsSource)
	url = models.URLField(max_length=200)
	pub_date = models.DateTimeField('date published')
	# photo / thumbnail
	summaryText = models.TextField()


class NewsEvent(NewsObject):
	# has many articles
	articles = models.ManyToManyField(Article)

class Comment(models.Model):
	text = models.TextField()
	date = models.DateTimeField('date posted')
	user = models.ForeignKey(User)
	commentee = models.ForeignKey(NewsObject)

	def __unicode__(self):
		return self.text

class Tag(models.Model):
	# Keep a fixed set of tags?
	text = models.CharField(max_length=33)
	tagees = models.ManyToManyField(NewsObject)

	def __unicode__(self):
		return self.text

class Topic(models.Model):
	name = models.CharField(max_length=33)
	tagees = models.ManyToManyField(Article)

class Rating(models.Model):
	RATING_CHOICES = [(1,"1"),(2,"2"),(3,"3"),(4,"4"),(5,"5")]
	rating = models.IntegerField(default=1, choices=RATING_CHOICES)
	rater = models.ForeignKey(User)
	ratee = models.ForeignKey(NewsObject)

	def __unicode__(self):
		return self.rater.name + " rated " + self.ratee.title + " " + str(self.rating)

class RecommendationBundle(models.Model):
	user = models.ForeignKey(User)

	# THESE ARE OBVIOUSLY DUMMY METHODS RITE DOODS?
	def articleRecommendations(self):
		return [1,2,3,4,5]

	def newsSourceRecommendations(self):
		return [1,2,3]

	def newsFeedRecommendations(self):
		return [1,2]

	def __unicode__(self):
		return self.user.name + " A:" + str(self.articleRecommendations) + " NSR:" + str(self.newsSourceRecommendations) + " NFR:" + str(self.newsFeedRecommendations)

