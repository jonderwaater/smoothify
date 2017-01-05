import requests
from upload import upload
from smoothen import smoothengpx
from stravalib import Client


def uploadhelper(args):

    client = Client(args[0])

    activity_id = upload(client, args[1], args[2], args[3], args[4], args[5], args[6], args[7])

    return activity_id


def smoothenhelper(args):

    smoothened_data = smoothengpx(args[0])

    return smoothened_data





