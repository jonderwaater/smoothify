from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import smoothify.views

from django.core.urlresolvers import reverse_lazy

urlpatterns = [
    url(r'^$', smoothify.views.index, name='index'),
    url(r'^token/$', smoothify.views.token, name='token'),
    url(r'^mytoken/$', smoothify.views.mytoken, name='mytoken'),
    url(r'^image/$', smoothify.views.image, name='image'),
    url(r'^gpxin/$', smoothify.views.gpxin, name='gpxin'),
    url(r'^gpxout/$', smoothify.views.gpxout, name='gpxout'),
    url(r'^overview/$', smoothify.views.overview, name='overview'),
    url(r'^activity/$', smoothify.views.activity, name='activity'),
    url(r'^process/$', smoothify.views.process, name='process'),
    url(r'^gpxupload/$', smoothify.views.gpxupload, name='gpxupload'),
    url(r'^wait/$', smoothify.views.wait, name='wait'),
    url(r'^waitprocess/$', smoothify.views.waitprocess, name='waitprocess'),
    url(r'^fail/$', smoothify.views.fail, name='fail'),
    url(r'^db', smoothify.views.db, name='db'),
]
