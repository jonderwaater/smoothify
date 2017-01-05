from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import hello.views

from django.core.urlresolvers import reverse_lazy

urlpatterns = [
    url(r'^$', hello.views.index, name='index'),
    url(r'^token/$', hello.views.token, name='token'),
    url(r'^image/$', hello.views.image, name='image'),
    url(r'^gpxin/$', hello.views.gpxin, name='gpxin'),
    url(r'^gpxout/$', hello.views.gpxout, name='gpxout'),
    url(r'^overview/$', hello.views.overview, name='overview'),
    url(r'^activity/$', hello.views.activity, name='activity'),
    url(r'^process/$', hello.views.process, name='process'),
    url(r'^gpxupload/$', hello.views.gpxupload, name='gpxupload'),
    url(r'^wait/$', hello.views.wait, name='wait'),
    url(r'^waitprocess/$', hello.views.waitprocess, name='waitprocess'),
    url(r'^fail/$', hello.views.fail, name='fail'),
    url(r'^db', hello.views.db, name='db'),
]
