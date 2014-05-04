from __future__ import absolute_import
from celery import shared_task, Task
from celery.registry import tasks
from time import sleep
from nf_server.models import NewsObject, Article

#from sklearn.linear_model import SGDClassifier
#from sklearn.externals import joblib

@shared_task
def slowAdd(x,y):
	#sleep(5)
	return NewsObject.objects.all()[0].title

@shared_task
def mul(x,y):
	return x * y

@shared_task
def xsum(numbers):
	return sum(numbers)

class ClassifierTask(Task):
	abstract = True
	_classifiers = None
	topics = ["politics", "sports"]

	@property
	def classifiers(self):
		if self._classifiers is None:
			self._classifiers = {}
			for topic in self.topics:
				try:
					self._classifiers[topic] = joblib.load("./brains/%sClassifier.pkl" % topic)
					print "using trained %s classifier" % topic
				except:
					print "building new %s classifier..." % topic
					self._classifiers[topic] = SGDClassifier(loss="hinge", penalty="l2")
					# actually train it...
					joblib.dump(self._classifiers[topic], "./brains/%sClassifier.pkl" % topic)
		return self._classifiers

@shared_task(base=ClassifierTask)
def classify(articleId):
	try:
		article = Article.objects.get(id=articleId)
		print "found article. classifying..."
	except:
		print "could not find article with id " + str(articleId)
		return
	#print classify.classifier
	return articleId

@shared_task(base=ClassifierTask)
def trainClassifier(articleId, topics):
	for topic in topics:
		if topic in classify.topics:
			print "updating %s classifier" % topic
			joblib.dump(classify.classifiers[topic], "./brains/%sClassifier.pkl" % topic)
		else:
			print "%s is not a valid topic" % topic
	return







