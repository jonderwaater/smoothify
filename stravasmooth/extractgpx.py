#!/usr/bin/env python2
from __future__ import print_function

from stravalib import Client, exc
#from sys import stderr, stdin
import sys
from tempfile import NamedTemporaryFile
import os.path
import argparse
import requests
import datetime


try:
    import configparser
    cp = configparser.ConfigParser()
except:
    import ConfigParser
    cp = ConfigParser.ConfigParser()
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

#####


def intro(file):
    file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    file.write("<gpx creator=\"stravasmooth\" version=\"0.0.1\" xmlns=\"http://www.topografix.com/GPX/1/1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd\">\n")
    file.write(" <metadata>\n")
    file.write("  <time>")
    return


def insert_date_stamp(file,date_stamp):
    date_stamp = date_stamp.replace(" ","T")
    date_stamp = date_stamp.replace("+00:00","Z")
    file.write(date_stamp)
    file.write("</time>\n")
    return


def start_segment(file,name,desc):
    file.write(" </metadata>\n")
    file.write(" <trk>\n")
    file.write('  <name>{}</name>\n'.format(name))
    file.write('  <desc>{}</desc>\n'.format(desc))
    file.write("  <trkseg>\n")
    return


def insert_datapoint(file,lat,lon,ele,time):
    file.write('   <trkpt lat=\"{0:.7f}\"'.format(lat))
    file.write('  lon=\"{0:.7f}\">\n'.format(lon))
    file.write('    <ele>{0:.2f}</ele>\n'.format(ele))
    file.write("    ")
    ts = '<time>{}Z</time>\n'.format(time)
    ts = ts.replace(" ","T")
    file.write(ts)
    #file.write('    <time>{}Z</time>\n'.format(time))
    file.write("   </trkpt>\n")
    return

def end_segment(file):
    file.write("  </trkseg>\n")
    file.write(" </trk>\n")
    file.write("</gpx>\n")

    return

#####

def getactivity(activity_id=None,client=None) :
    if client == None :
        client = Client(access_token=os.environ['CLIENT_TOKEN'])

    if activity_id == None :
        activities = client.get_activities(limit=1)
        for i in activities :
            activity = i

    else :
        try :
            activity = client.get_activity(activity_id)
        except :
            return int(0)

    athlete = activity.athlete

    if not athlete.is_authenticated_athlete() :
        return int(1)


    return activity



def extractgpx(activity,client):

    types = ['time', 'latlng', 'altitude' ]
    
    with open('{}.gpx'.format(activity.id), 'w') as file :
    
        intro(file)
    
        timestamp=str(activity.start_date)
    
        insert_date_stamp(file,timestamp)
    
        timestamp = timestamp.replace("+00:00","")
    
        datestring=timestamp.split(" ")[0].split("-")  
        timestring=timestamp.split(" ")[1].split(":")
    
        start_segment(file,activity.name,activity.description)
    
        streams = client.get_activity_streams(activity.id, types=types, resolution='high')
        latlng = streams['latlng'].data
        time = streams['time'].data
        altitude = streams['altitude'].data
        distance = streams['distance'].data
    
        start_date = datetime.datetime(int(datestring[0]), int(datestring[1]), int(datestring[2]), int(timestring[0]), int(timestring[1]), int(timestring[2]))
    
        print("Processing activity \"",activity.name,"\" from date",start_date)
    
        for it in range(0,len(latlng)):
            lat = latlng[it][0]
            lon = latlng[it][1]
            t = start_date + datetime.timedelta(seconds=time[it])
            alt = altitude[it]
            insert_datapoint(file,lat,lon,alt,t)
    
        end_segment(file)



if __name__ == "__main__":

    activity_id = None

    if len(sys.argv) > 1 :
        activity_id = sys.argv[1]

    if activity_id == None :
        print("Retrieving last activity")
    else :
        print("Retrieving activity",activity_id)

    activity = getactivity()

    if activity.is_authenticated_athlete() :
        extractgpx(client,activity)
    else :
        print("Activity does not belong to user")

#####

