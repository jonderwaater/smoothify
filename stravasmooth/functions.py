from stravalib import Client, exc
from gpxpy import geo as mod_geo
import multiprocessing as mp
from datetime import datetime
import xml.etree.ElementTree as ET
import os

def gettoken():
    token=None
    with open(os.path.expanduser('~/.stravasmooth'), 'r') as f:
        c = f.readlines()
    for line in c :
        words = line.split("=")
        if words[0] == "STRAVASMOOTH_TOKEN" :
            token = words[1]

    return token


def getactivity(activity_id=0,client=None) :
    if client == None :
        token = gettoken()
        client = Client(access_token=token)

    if activity_id == 0 :
        activities = client.get_activities(limit=1)
        for i in activities :
            activity = i

    else :
        try :
            activity = client.get_activity(activity_id)
        except :
            print('Activity not found')
            return int(0),client

    athlete = activity.athlete

    if not athlete.is_authenticated_athlete() :
        print('Activity does not belong to user')
        return int(1),client

    return activity,client


def distance(lat,lon,ele):

    distance = 0
    if not ele == None :
        for i in range(len(lat)-1) :
            d = mod_geo.distance(lat[i],lon[i],ele[i],lat[i+1],lon[i+1],ele[i+1])
            distance= distance + d
    else :
        for i in range(len(lat)-1) :
            d = mod_geo.distance(lat[i],lon[i],None,lat[i+1],lon[i+1],None)
            distance= distance + d

    return distance


def plot(outfile,lat,lon,latsmooth,lonsmooth) :
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt


    fig = plt.figure(facecolor = '0.05')
    ax = plt.Axes(fig, [0., 0., 1., 1.], )
    #ax.set_aspect('equal')
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.plot(lonsmooth, latsmooth, '-',zorder=1)
    plt.scatter(lon, lat, s=1, color='red', edgecolor='',zorder=2)
    plt.savefig(outfile, facecolor = fig.get_facecolor(), bbox_inches='tight', pad_inches=0, dpi=900)
    print('File created: {}'.format(outfile))


def runplot(args) :
    proc=mp.Process(target=plot,args=args)
    proc.daemon=True
    proc.start()
    proc.join()


def getarraysfile(gpxdata):

    lat = []
    lon = []
    ele = []
    time = []

    root = ET.fromstring(gpxdata)

    for trkseg in root.iter('{http://www.topografix.com/GPX/1/1}trkseg'):
        for point in trkseg :
            lat.append(float(point.get('lat')))
            lon.append(float(point.get('lon')))
            ele.append(float(point[0].text))
            ptime = point.find('{http://www.topografix.com/GPX/1/1}time')
            time.append(ptime.text)
            #print point.attrib,point[1].text
            #time.append(datetime.strptime(point[1].text, "%Y-%m-%dT%H:%M:%SZ"))

    return lat,lon,ele,time

def getarraysfilename(gpxfilename):
    with open(gpxfilename, 'r') as f:
      gpxdata=f.read()
    lat,lon,ele,time = getarraysfile(gpxdata)
    return lat,lon,ele,time

def getdistancefilename(gpxfilename):
    lat,lon,ele,time = getarraysfilename(gpxfilename)
    return distance(lat,lon,ele)

def plotfiles(outfile,infile1,infile2) :
    lat1,lon1,ele1,time1 = getarraysfilename(infile1)
    lat2,lon2,ele2,time2 = getarraysfilename(infile2)
    plot(outfile,lat1,lon1,lat2,lon2)


def getgpxinfofilename(gpxfilename):

    with open(gpxfilename, 'r') as f:
      gpxdata=f.read()

    root = ET.fromstring(gpxdata)

    title = None
    desc = None
    for trk in root.iter('{http://www.topografix.com/GPX/1/1}trk'):
        nametag = trk.find('{http://www.topografix.com/GPX/1/1}name')
        desctag = trk.find('{http://www.topografix.com/GPX/1/1}desc')
        if not nametag == None :
            title = nametag.text
        if not desctag == None :
            desc = desctag.text

    return gpxdata,title,desc


