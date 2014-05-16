from django.conf.urls import patterns, url
from nf_server import views

urlpatterns = patterns('',
    url(r'^nf_server$', views.nf_server, name='nf_server'),
    url(r'^$', views.index, name='index'),
    url(r'^about', views.about, name='about'),
    url(r'^source/(?P<source_id>\d+)/', views.source, name='source'),
    url(r'^edit/(?P<feed_id>\d+)/', views.edit, name='edit'),
    url(r'^feed/(?P<feed_id>\d+)/', views.feed, name='feed'),
    url(r'^event/(?P<event_id>\d+)/', views.event, name='event'),
    url(r'^create_event$', views.createEvent, name='create_event'),
    url(r'^new_event$', views.newEvent, name='new_event'),
    url(r'^article/(?P<article_id>\d+)/', views.article, name='article'), 
    url(r'^search/', views.search, name='search'),
    url(r'^fire_search/(?P<query>.+)/', views.fireSearch, name='fire_search'),
)