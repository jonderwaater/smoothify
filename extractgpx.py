#!/usr/bin/env python2
from __future__ import print_function

from stravalib import Client, exc
from sys import stderr, stdin
from tempfile import NamedTemporaryFile
import webbrowser, os.path, ConfigParser, gzip
import argparse
import numpy as np
from cStringIO import StringIO
import requests
import datetime
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

#####

mygpx = "latest.gpx"

def intro():
    with open(mygpx, 'w') as file :
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        file.write("<gpx creator=\"strava.com Android\" version=\"1.1\" xmlns=\"http://www.topografix.com/GPX/1/1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd\">\n")
        file.write(" <metadata>\n")
        file.write("  <time>")
    file.close
    return


def insert_date_stamp(date_stamp):
    with open(mygpx, 'a') as file :
        date_stamp = date_stamp.replace(" ","T")
        date_stamp = date_stamp.replace("+00:00","Z")
        file.write(date_stamp)
        file.write("</time>\n")
        file.close
    return


def start_segment(name):
    with open(mygpx, 'a') as file :
        file.write(" </metadata>\n")
        file.write(" <trk>\n")
        file.write('  <name>{}</name>\n'.format(name))
        file.write("  <trkseg>\n")

        file.close
    return


def insert_datapoint(lat,lon,ele,time):
    with open(mygpx, 'a') as file :
        file.write('   <trkpt lat=\"{}\"'.format(lat))
        file.write('  lon=\"{}\">\n'.format(lon))
        file.write('    <ele>{}</ele>\n'.format(ele))
        file.write("    ")
        ts = '<time>{}Z</time>\n'.format(time)
        ts = ts.replace(" ","T")
        file.write(ts)
        #file.write('    <time>{}Z</time>\n'.format(time))
        file.write("   </trkpt>\n")

        file.close
        return

def end_segment():
    with open(mygpx, 'a') as file :
        file.write("  </trkseg>\n")
        file.write(" </trk>\n")
        file.write("</gpx>\n")

        file.close
        return


#####

# Authorize Strava

cid = 3163 # CLIENT_ID
cp = ConfigParser.ConfigParser()
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
        print("NOT AUTHORIZED, GET YOUR TOKEN FROM https://stravacli-dlenski.rhcloud.com/", file=stderr)
    else:
        if not cp.has_section('API'):
            cp.add_section('API')
        if not 'ACCESS_TOKEN' in cp.options('API') or cp.get('API', 'ACCESS_TOKEN', None)!=cat:
            cp.set('API', 'ACCESS_TOKEN', cat)
            cp.write(open(os.path.expanduser('~/.stravacli'),"w"))
        break

print("Authorized to access account of {} {} (id {:d}).".format(athlete.firstname, athlete.lastname, athlete.id))


activities = client.get_activities(limit=1)
#assert len(list(activities)) == 1

types = ['time', 'latlng', 'altitude' ]
for activity in activities:

    intro()

    timestamp=str(activity.start_date)

    insert_date_stamp(timestamp)

    timestamp = timestamp.replace("+00:00","")

    datestring=timestamp.split(" ")[0].split("-")  
    timestring=timestamp.split(" ")[1].split(":")

    start_segment(activity.name)

    streams = client.get_activity_streams(activity.id, types=types, resolution='high')
    latlng = streams['latlng'].data
    time = streams['time'].data
    altitude = streams['altitude'].data

    start_date = datetime.datetime(int(datestring[0]), int(datestring[1]), int(datestring[2]), int(timestring[0]), int(timestring[1]), int(timestring[2]))

    print(start_date)

    info = np.transpose(latlng)
    for it in range(0,len(info[0])):
        lat = info[0][it]
        lon = info[1][it]
        t = start_date + datetime.timedelta(seconds=time[it])
        alt = altitude[it]
        insert_datapoint(lat,lon,alt,t)

    #client.delete_activity(activity.id)

    end_segment()


#####

