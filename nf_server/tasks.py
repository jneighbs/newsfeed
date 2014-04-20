from __future__ import absolute_import
from celery import shared_task
from time import sleep

@shared_task
def slowAdd(x,y):
	sleep(10)
	return x+y

@shared_task
def mul(x,y):
	return x * y

@shared_task
def xsum(numbers):
	return sum(numbers)