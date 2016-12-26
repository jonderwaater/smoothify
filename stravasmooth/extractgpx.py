#!/usr/bin/env python2
from __future__ import print_function

from stravalib import Client, exc
#from sys import stderr, stdin
import sys
from tempfile import NamedTemporaryFile
import webbrowser
import os.path
import argparse
from cStringIO import StringIO
import requests
import datetime
try:
    import configparser
    cp = configparser.configparser()
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
    file.close
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

# Authorize Strava

def strava_connect():
    cid = 3163 # CLIENT_ID
    cp.read(os.path.expanduser('~/.stravacli'))
    cat = None
    if cp.has_section('API'):
        cat = cp.get('API', 'ACCESS_TOKEN') if 'access_token' in cp.options('API') else None
    
    while True:
        client = Client(cat)
        try:
            athlete = client.get_athlete()
        except requests.exceptions.ConnectionError:
            print("Could not connect to Strava API")
        except Exception as e:
            print("NOT AUTHORIZED, GET YOUR TOKEN FROM https://stravacli-dlenski.rhcloud.com/ AND SAVE THE THREE LINES TO FILE ~/.stravacli", file=stderr)
            return 0
        else:
            if not cp.has_section('API'):
                cp.add_section('API')
            if not 'ACCESS_TOKEN' in cp.options('API') or cp.get('API', 'ACCESS_TOKEN', None)!=cat:
                cp.set('API', 'ACCESS_TOKEN', cat)
                cp.write(open(os.path.expanduser('~/.stravacli'),"w"))
            break
    
    print("Authorized to access account of {} {} (id {:d}).".format(athlete.firstname, athlete.lastname, athlete.id))
    return client


def extractgpx(activity_id=0):

    client = strava_connect()
    if client == 0 :
        return ""
    
    if activity_id == 0 :
        activities = client.get_activities(limit=1)
        for i in activities :
            activity = i

    else :
        activity = client.get_activity(activity_id)

    #assert len(list(activities)) == 1
    
    types = ['time', 'latlng', 'altitude' ]
    
    name = activity.name
    name = name.replace(" ","_")
    
    with open(name+".gpx", 'w') as file :
    
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
    
        start_date = datetime.datetime(int(datestring[0]), int(datestring[1]), int(datestring[2]), int(timestring[0]), int(timestring[1]), int(timestring[2]))
    
        print("Processing activity \"",name,"\" from date",start_date)
    
        info = zip(*latlng)
        #info = np.transpose(latlng)
    
        for it in range(0,len(info[0])):
            lat = info[0][it]
            lon = info[1][it]
            t = start_date + datetime.timedelta(seconds=time[it])
            alt = altitude[it]
            insert_datapoint(file,lat,lon,alt,t)
    
    
        end_segment(file)

        return activity

if __name__ == "__main__":

    activity_id = 0

    if len(sys.argv) == 2 :
        activity_id = sys.argv[1]

    if activity_id == 0 :
        print("Retreiving last activity")
    else :
        print("Retreiving activity",activity_id)

    extractgpx(activity_id)

#####

