from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import stravasmooth.views

from django.core.urlresolvers import reverse_lazy

urlpatterns = [
    url(r'^$', stravasmooth.views.index, name='index'),
    url(r'^token/$', stravasmooth.views.token, name='token'),
    url(r'^mytoken/$', stravasmooth.views.mytoken, name='mytoken'),
    url(r'^image/$', stravasmooth.views.image, name='image'),
    url(r'^gpxin/$', stravasmooth.views.gpxin, name='gpxin'),
    url(r'^gpxout/$', stravasmooth.views.gpxout, name='gpxout'),
    url(r'^overview/$', stravasmooth.views.overview, name='overview'),
    url(r'^activity/$', stravasmooth.views.activity, name='activity'),
    url(r'^process/$', stravasmooth.views.process, name='process'),
    url(r'^gpxupload/$', stravasmooth.views.gpxupload, name='gpxupload'),
    url(r'^wait/$', stravasmooth.views.wait, name='wait'),
    url(r'^waitprocess/$', stravasmooth.views.waitprocess, name='waitprocess'),
    url(r'^fail/$', stravasmooth.views.fail, name='fail'),
    url(r'^db', stravasmooth.views.db, name='db'),
]
