from django.db import models
from django.forms import ModelForm
from django import forms
# Create your models here.

# An abstract object that has a title and has many comments and tags and ratings
class NewsObject(models.Model):
	title = models.CharField(max_length=200)

	def __unicode__(self):
		return self.title

class NewsSource(NewsObject):
	country = models.CharField(max_length=30)
	description = models.TextField()

	def allText(self):
		return self.title + " " + self.description

class NewsFeed(NewsObject):
	# has many newsSources
	newsSources = models.ManyToManyField(NewsSource)
	# belongs to a user
	owner = models.ForeignKey('User', related_name='ownedNewsFeeds')

	description = models.TextField()
	
	# user_set
	# tag_set

	# DO LATER
	# has many topic filters
	# has a user filter?

	def allText(self):
		return self.title + " " + self.description

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
	summaryText = models.CharField(max_length=200)

	def allText(self):
		return self.title + " " + self.summaryText

class NewsEvent(NewsObject):
	# has many articles
	eventTag = models.CharField(max_length=33)
	articles = models.ManyToManyField(Article, related_name='news_event')
	pendingArticles = models.ManyToManyField(Article, related_name='pending_news_event')
	# timelineentry_set to get timeline entries
	# tag_set to get tags
	owner = models.ForeignKey(User, related_name='owned_events')
	leadEditors = models.ManyToManyField(User, related_name='lead_edited_events')
	editors = models.ManyToManyField(User, related_name='edited_events')

	def allText(self):
		return self.title + " " + self.eventTag

class TimelineEntry(models.Model):
	text = models.TextField()
	date = models.DateTimeField('date updated')
	event = models.ForeignKey(NewsEvent)
	def __unicode__(self):
		return self.text

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

class NewsEventForm(ModelForm):

	articles = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple(), required=False)
	pendingArticles = forms.ModelMultipleChoiceField(queryset=None, required=False)
	leadEditors = forms.ModelMultipleChoiceField(queryset=None, required=False)
	editors = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple(), required=False)

	def __init__(self, *args, **kwargs):
		super(NewsEventForm, self).__init__(*args, **kwargs)
		for name, field in self.fields.items():
			if field.widget.__class__ == forms.widgets.TextInput:
				if field.widget.attrs.has_key('class'):
					field.widget.attrs['class'] += ' form-control'
				else:
					field.widget.attrs.update({'class':'form-control'})
			if field.label == 'EventTag':
				field.widget.attrs.update({'placeholder':'Event Tag...'})
			elif field.label == 'Title':
				field.widget.attrs.update({'placeholder':'Title...'})
	class Meta:
		model = NewsEvent
		fields = ['title', 'eventTag', 'articles', 'pendingArticles', 'owner', 'leadEditors', 'editors']

	#timelineEntries = forms.ModelMultipleChoiceField(queryset=TimelineEntry.objects.filter(event=self.id))
	#tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(tagee=self.id))




