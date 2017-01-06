#!/usr/bin/env python2
import gpxpy
import gpxpy.geo as mod_geo
import re
import fileinput
import sys
import tempfile


def smoothen(infile,algo=1):
    infile.seek(0)
    gpx_file_data=infile.read()
    return gpx_file_data


def smoothengpx(gpx_file_smooth_data,algo=1):


    lat = []
    lon = []
    
    nsection=9
    
    infile = tempfile.TemporaryFile()
    infile.write(gpx_file_smooth_data)
    infile.seek(0)
    gpx = gpxpy.parse(infile)
    infile.seek(0)

    
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lat.append(point.latitude)
                lon.append(point.longitude)
    
    latsmooth = list(lat)
    lonsmooth = list(lon)
    
    
    #infile.seek(0)
    # this is the smoothening algorithm
    for sectionstart in range(0,len(lon)-1-nsection):
        centslice = int(sectionstart+(nsection-1)/2)
        lonslice = lon[sectionstart:sectionstart+nsection]
        latslice = lat[sectionstart:sectionstart+nsection]

        if int(algo) == 0 :
            import numpy as np
            z = np.polyfit(lonslice,latslice,1)
            p = np.poly1d(z)
            xp = np.linspace(lonslice[0],lonslice[nsection-1], nsection)
            stepsize = (lonslice[nsection-1]-lonslice[0])/100
            dmin=1000;
            for i in range(1,100):
                d = mod_geo.distance(lonslice[0]+stepsize*i,p(lonslice[0]+stepsize*i),None,lonslice[(nsection-1)/2],latslice[(nsection-1)/2],None)
                if d < dmin:
                    dmin = d
                    lonsmooth[centslice] = lonslice[0]+stepsize*i
                    latsmooth[centslice] = p(lonslice[0]+stepsize*i)

        if int(algo) == 1 :
            lonsmooth[centslice] = sum(lonslice)/len(lonslice)
            latsmooth[centslice] = sum(latslice)/len(latslice)
        
        
        for line in infile:
            linevalues = re.findall("\d+\.\d+",line)
            if(len(linevalues)==2):
                thislat = float(linevalues[0])
                thislon = float(linevalues[1])
    
                data={lat[centslice],lon[centslice]}
    
                if thislat == lat[centslice]:
                    if thislon == lon[centslice]:
                        newline = '   <trkpt lat="{0:.7f}" lon="{1:.7f}">\n'.format(latsmooth[centslice],lonsmooth[centslice])
                        gpx_file_smooth_data = gpx_file_smooth_data.replace(line,newline)
                        break

    return gpx_file_smooth_data
                            

def writeoutput(filename,gpx) :
    with open(filename, 'w') as file :
        file.write(gpx)



def getgpxinfile(filename) :
    gpx_file = open(filename, 'r')
    gpx = gpxpy.parse(gpx_file)
    return gpx



def getgpx(filename) :
    filename.seek(0)
    gpx = gpxpy.parse(filename)
    return gpx



if __name__ == "__main__":

    if len(sys.argv) > 1 :
        activity = sys.argv[1]
        gpx_filename='{}.gpx'.format(activity)
        infile = open(gpx_filename, 'r')
        graph = True
        if len(sys.argv) > 2 :
            graph = sys.argv[2]
        if len(sys.argv) == 4 :
            algo = sys.argv[3]

    gpxout = smoothen(infile)

    writeoutput('{}_smooth.gpx'.format(activity), gpxout)


