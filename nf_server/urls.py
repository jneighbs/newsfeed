from django.conf.urls import patterns, url

from nf_server import views

urlpatterns = patterns('',
    url(r'^nf_server$', views.nf_server, name='nf_server'),
    url(r'^event', views.event, name='event'),
    url(r'^article', views.article, name='article'),
    url(r'^$', views.index, name='index'),
)