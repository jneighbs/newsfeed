from django.conf.urls import patterns, url

from nf_server import views

urlpatterns = patterns('',
    url(r'^nf_server$', views.nf_server, name='nf_server'),
    url(r'^event/(?P<event_id>\d+)/', views.event, name='event'),
    url(r'^feed/(?P<feed_id>\d+)/', views.feed, name='feed'),
    url(r'^create_event$', views.createEvent, name='create_event'),
    url(r'^create_event/(?P<event_id>\d+)/', views.createEvent, name='edit_event'),
    url(r'^new_event$', views.newEvent, name='new_event'),
    url(r'^article/(?P<article_id>\d+)/', views.article, name='article'),
    url(r'^$', views.index, name='index'),
)