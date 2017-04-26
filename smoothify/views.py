from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse,resolve
from django import forms
from django.conf import settings
from django import http
from django.shortcuts import redirect
from django.views import generic

from rq import Queue
from worker import conn

from wsgiref.util import FileWrapper
import time
import os

from stravalib import Client
#import gpxpy

import extractgpx,smoothen,functions
from utils import uploadhelper,smoothenhelper
import xml.etree.ElementTree as ET

from .models import Greeting
#import resource

class ActivityIdForm(forms.Form):
    activity_id = forms.IntegerField()

global activity_name
queue = Queue(connection=conn)



def index(request):

    client_id = os.environ['SMOOTHIFY_ID']

    client = Client()
    
    redirect_uri = request.build_absolute_uri('/token/')
    url = client.authorization_url(client_id=client_id, redirect_uri=redirect_uri, scope='view_private,write')

    #print '(index) Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    return render(request, 'index.html',{'url':url})



def token(request):

    code = request.GET.get("code", None)
    
    if not code:
        return HttpResponse('<a href='+reverse('index')+'>Failed, try again.</a>')
    else :
        client = Client()
        access_token = client.exchange_code_for_token(client_id=os.environ['SMOOTHIFY_ID'],
                                                      client_secret=os.environ['SMOOTHIFY_SECRET'],
                                                      code=code)

        request.session['SMOOTHIFY_TOKEN'] = access_token

        athlete = client.get_athlete()
        request.session['ATHLETE_FIRSTNAME'] = athlete.firstname


        request.session['ACTIVITY_ERROR']=None
        return HttpResponseRedirect('/activity/')

def mytoken(request):

    return render(request, 'mytoken.html',{'token':request.session['SMOOTHIFY_TOKEN']})


def activity(request):

    request.session['ACTIVITY_ID'] = 0

    if request.method == 'POST':
        form = ActivityIdForm(request.POST)
        if form.is_valid():
            request.session['ACTIVITY_ID'] = form.cleaned_data['activity_id']
            return HttpResponseRedirect('/process/')
    else :
        form = ActivityIdForm()

    return render(request, 'name.html', {'form':form,'athlete_firstname':request.session['ATHLETE_FIRSTNAME'],'activityurl':reverse('process'),'activity_error':request.session['ACTIVITY_ERROR'],'mytokenurl':reverse('mytoken')})



def process(request):

    client = Client(request.session['SMOOTHIFY_TOKEN'])

    activity_id = int(request.session['ACTIVITY_ID'])
    activity,client = functions.getactivity(activity_id,client)

    if activity == 0 :
        request.session['ACTIVITY_ERROR']=0
        return HttpResponseRedirect('/activity/')


    if activity == 1 :
        request.session['ACTIVITY_ERROR']=1
        return HttpResponseRedirect('/activity/')

    gpxfilename = extractgpx.extractgpx(activity, client)

    request.session['ACTIVITY_NAME']     =        activity.name
    request.session['TIMESTAMP']         =    str(activity.start_date)
    request.session['DISTANCE_STRAVA']   =  float(activity.distance)
    request.session['ACTIVITY_TYPE']     =        activity.type
    request.session['ACTIVITY_PRIVATE']  =        activity.private
    request.session['ACTIVITY_ID']       =        activity.id

    arg1 = smoothen.getgpxstring(gpxfilename)

    job = queue.enqueue(smoothenhelper, (arg1,))
    request.session['SMOOTHENJOB_ID'] = job.id

    return HttpResponseRedirect('/waitprocess/')




def waitprocess(request):
    jobid = request.session['SMOOTHENJOB_ID']
    job = queue.fetch_job(jobid)
    if job.result == None :
        time.sleep(3)
        return HttpResponseRedirect('/waitprocess/')

    smoothened_data, lat, lon, ele, latsmooth, lonsmooth, elesmooth = job.result
    smoothen.writeoutput('{}_smooth.gpx'.format(request.session['ACTIVITY_ID']),smoothened_data)

    request.session['DISTANCE_OLD'] = functions.distance(lat,lon,ele)
    request.session['DISTANCE_NEW'] = functions.distance(latsmooth,lonsmooth,elesmooth)

    args = ('{}.png'.format(request.session['ACTIVITY_ID']),lat,lon,latsmooth,lonsmooth,)
    functions.runplot(args)
    return HttpResponseRedirect('/overview/')



def image(request):
    pngfile = '{}.png'.format(request.session['ACTIVITY_ID'])
    with open(pngfile, "rb") as f:
        return HttpResponse(f.read(), content_type="image/png")



def gpxin(request):
    gpxfile = '{}.gpx'.format(request.session['ACTIVITY_ID'])
    return HttpResponse(FileWrapper(file(gpxfile)), content_type="text/plain")



def gpxout(request):
    gpxfile = '{}_smooth.gpx'.format(request.session['ACTIVITY_ID'])
    return HttpResponse(FileWrapper(file(gpxfile)), content_type="text/plain")



def overview(request):
    timestamp = request.session['TIMESTAMP']
    timestamp = timestamp.replace("+00:00","")
    distance  = float(request.session['DISTANCE_STRAVA'])
    distance_old  = request.session['DISTANCE_OLD']
    distance_new  = request.session['DISTANCE_NEW']

    distance_old  = float('{0:.2f}'.format(distance_old))
    distance_new  = float('{0:.2f}'.format(distance_new))

    change_old = (distance_old-distance)/distance*100
    change_new = (distance_new-distance)/distance*100

    distance    = '{0:.2f}'.format(distance)
    change_old  = '{0:.2f}'.format(change_old)
    change_new  = '{0:.2f}'.format(change_new)

    return render(request, "results.html",{'activity_id':request.session['ACTIVITY_ID'],'activity_name':request.session['ACTIVITY_NAME'],'timestamp':timestamp,'distance':distance,'distance_old':distance_old,'distance_new':distance_new,'change_old':change_old,'change_new':change_new,'ori':reverse('gpxin'),'smo':reverse('gpxout'),'up':reverse('gpxupload'),'graph':reverse('image')})



def gpxupload(request):

    gpxfilename = '{}_smooth.gpx'.format(request.session['ACTIVITY_ID'])
    gpxfile, title, desc = functions.getgpxinfofilename(gpxfilename)

    overwrite = True
    args=(request.session['SMOOTHIFY_TOKEN'], gpxfile, title, desc, request.session['ACTIVITY_TYPE'], request.session['ACTIVITY_PRIVATE'], overwrite, request.session['ACTIVITY_ID'],)
    job = queue.enqueue(uploadhelper, args)
    request.session['UPLOADJOB_ID'] = job.id
    return HttpResponseRedirect('/wait/')



def wait(request):
    jobid = request.session['UPLOADJOB_ID']
    job = queue.fetch_job(jobid)
    time.sleep(5)
    if job.result == None :
        return HttpResponseRedirect('/wait/')

    activity_id = job.result

    if activity_id == 0 :
        return HttpResponseRedirect('/fail/')

    return redirect('http://strava.com/activities/{:d}'.format(activity_id))



def fail(request):
    response = HttpResponse()
    response.write('<pre> Oops! Something went wrong. </pre> </br>')
    response.write('<a href='+reverse('overview')+'>Go back to overview</a></br>')
    return response
    


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})



