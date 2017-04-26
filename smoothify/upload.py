from stravalib import Client, exc
from sys import stderr, stdin
import os.path
import argparse
import requests
import time
import xml.etree.ElementTree as ET
from . import functions

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


def main(arguments=""):


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
    g.add_argument('-i', '--ori-id', default=None, help='Id of original activity on Strava')

    if arguments == "" :  
        args = p.parse_args()
    else :
        args = p.parse_args(arguments.split(" "))

    overwrite = args.overwrite
    gpx_filename = args.filename
    activity_type = args.activity_type
    private = args.private
    ori_id = args.ori_id

    print('Uploading activity...')

    token = functions.gettoken()
    client = Client(access_token=token)
                                                                  
    gpxfile, title, desc = functions.getgpxinfofilename(gpx_filename)

    newactivity = upload(client, gpxfile, title, desc, activity_type, private, overwrite, ori_id)
    return newactivity

                                                                  
def upload(client, gpxfile, title, desc, activity_type, private, overwrite, duplicate_id=None):

    if desc == 'None' :
        desc = ''

    if not duplicate_id == None :
        if overwrite :
            print('Deleting activity {}'.format(duplicate_id))
            client.delete_activity(duplicate_id)
            time.sleep(1)

    try:
        upstat = client.upload_activity(gpxfile, 'gpx', title, desc, private=private, activity_type=activity_type)
        activity = upstat.wait()
    except exc.ActivityUploadFailed as e:
        words = e.args[0].split()
        if words[-4:-1]==['duplicate','of','activity']:
            print('Activity is duplicate')
            activity = client.get_activity(words[-1])
            if overwrite :
                activity = upload(client, gpxfile, title, desc, activity_type, private, overwrite, duplicate_id=activity.id)
                return activity
        else:
            raise

    webpage = 'https://www.strava.com/activities/{}'.format(activity.id)
    print('Activity available at: {}'.format(webpage))
    return activity



if __name__ == "__main__":
    main()
