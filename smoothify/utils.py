import requests
from upload import upload
from smoothen import runsmoothengpx
from stravalib import Client


def uploadhelper(args):

    client = Client(args[0])

    activity = upload(client, args[1], args[2], args[3], args[4], args[5], args[6], args[7])
    
    if activity :
        activity_id = activity.id
    else :
        activity_id = 0

    return activity_id


def smoothenhelper(args):

    smoothened_data, lat, lon, ele, latsmooth, lonsmooth, elesmooth = runsmoothengpx(args)

    return smoothened_data, lat, lon, ele, latsmooth, lonsmooth, elesmooth





