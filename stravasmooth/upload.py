#!/usr/bin/env python2

from stravalib import Client, exc
from sys import stderr, stdin
import os.path
import argparse
import requests
import gpxpy
import time

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


def main(arguments):


    p = argparse.ArgumentParser(description='''Uploads activities to Strava.''')
    p.add_argument('-f', '--filename' , default=0          , help="gpx filename.")
    p.add_argument('-o', '--overwrite', action='store_true', help="In case of duplicate, delete and replace original.")
    g = p.add_argument_group('Activity file details')
    g.add_argument('-p', '--private', action='store_true', help='Make activities private')
    g.add_argument('-A', '--activity-type', default=None, help='''Type of activity. If not specified, the default value is taken
                                                                  from user profile. Supported values:
                                                                  ride, run, swim, workout, hike, walk, nordicski, alpineski,
                                                                  backcountryski, iceskate, inlineskate, kitesurf, rollerski,
                                                                  windsurf, workout, snowboard, snowshoe''')

    args = p.parse_args(arguments.split(" "))

    overwrite = args.overwrite
    gpx_filename = args.filename
    activity_type = args.activity_type
    private = args.private

    client = Client(access_token=os.environ['CLIENT_TOKEN'])
                                                                  
    gpx_file = open(gpx_filename, 'r')
    gpx = gpxpy.parse(gpx_file)
        
    gpx_file.seek(0,0)
    gpxfile = gpx_file.read()

    for track in gpx.tracks :
        title = track.name
        desc = track.description

    upload(client, gpxfile, title, desc, activity_type, private, overwrite)

                                                                  
def upload(client, gpxfile, title, desc, activity_type, private, overwrite, duplicate_id=None):

    if desc == 'None' :
        desc = ''
        

    # upload activity

    if not duplicate_id == None :
        if overwrite :
            client.delete_activity(duplicate_id)
            time.sleep(1)
            upstat = client.upload_activity(gpxfile, 'gpx', title, desc, private=private, activity_type=activity_type)
            activity = upstat.wait()
            return activity.id

    return 0


    try:
        upstat = client.upload_activity(gpxfile, 'gpx', title, desc, private=private, activity_type=activity_type)
        activity = upstat.wait()
    except exc.ActivityUploadFailed as e:
        words = e.args[0].split()
        if words[-4:-1]==['duplicate','of','activity']:
            activity = client.get_activity(words[-1])
            if overwrite :
                print("Uploading duplicate, overwriting original")
                activity_id = activity.id
                client.delete_activity(activity_id)
                try:
                    upstat = client.upload_activity(gpxfile, 'gpx' , title, desc, private=private, activity_type=activity_type)
                    activity = upstat.wait()
                    return activity
                except exc.ActivityUploadFailed as e:
                    print("Upload failed")
        else:
            raise
    
    return activity


if __name__ == "__main__":
    main(arguments)
