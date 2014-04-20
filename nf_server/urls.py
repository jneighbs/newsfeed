from django.conf.urls import patterns, url

from nf_server import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)