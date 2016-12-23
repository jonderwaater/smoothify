#!/usr/bin/env python2
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import gpxpy
import gpxpy.geo as mod_geo
import numpy as np
from numpy import pi, r_
import shutil
import re
import fileinput

def smoothen(activity,graph=True):

    lat = []
    lon = []
    latsmooth = []
    lonsmooth = []
    
    fig = plt.figure(facecolor = '0.05')
    ax = plt.Axes(fig, [0., 0., 1., 1.], )
    ax.set_aspect('equal')
    ax.set_axis_off()
    fig.add_axes(ax)
    
    nsection=9
    
    gpx_filename=activity+".gpx"
    gpx_filename_out=activity+"_smooth.gpx"
    
    gpx_file = open(gpx_filename, 'r')
    gpx = gpxpy.parse(gpx_file)
    
    shutil.copyfile(gpx_filename,gpx_filename_out)
    
    gpx_file_smooth = open(gpx_filename_out, 'r')
    
    gpx_file_smooth_data = None 
    with open(gpx_filename_out, 'r') as file :
        gpx_file_smooth_data = file.read()
    
    
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lat.append(point.latitude)
                lon.append(point.longitude)
    
    latsmooth = list(lat)
    lonsmooth = list(lon)
    
    
    # this is the smoothening algorithm
    for sectionstart in range(0,len(lon)-1-nsection):
        lonslice = lon[sectionstart:sectionstart+nsection]
        latslice = lat[sectionstart:sectionstart+nsection]
        z = np.polyfit(lonslice,latslice,1)
        p = np.poly1d(z)
        xp = np.linspace(lonslice[0],lonslice[nsection-1], nsection)
        stepsize = (lonslice[nsection-1]-lonslice[0])/100
        dmin=1000;
        for i in range(1,100):
            d = mod_geo.distance(lonslice[0]+stepsize*i,p(lonslice[0]+stepsize*i),None,lonslice[(nsection-1)/2],latslice[(nsection-1)/2],None)
            if d < dmin:
                dmin = d
                lonsmooth[sectionstart+(nsection-1)/2] = lonslice[0]+stepsize*i
                latsmooth[sectionstart+(nsection-1)/2] = p(lonslice[0]+stepsize*i)
    
        for line in gpx_file_smooth:
            linevalues = re.findall("\d+\.\d+",line)
            if(len(linevalues)==2):
                thislat = float(linevalues[0])
                thislon = float(linevalues[1])
    
                data={lat[sectionstart+(nsection-1)/2],lon[sectionstart+(nsection-1)/2]}
    
                if thislat == lat[sectionstart+(nsection-1)/2]:
                    if thislon == lon[sectionstart+(nsection-1)/2]:
                        newline = '   <trkpt lat="{}" lon="{}">\n'.format(latsmooth[sectionstart+(nsection-1)/2],lonsmooth[sectionstart+(nsection-1)/2])
                        gpx_file_smooth_data = gpx_file_smooth_data.replace(line,newline)
                        break
                            
    
    with open(gpx_filename_out, 'w') as file :
        file.write(gpx_file_smooth_data)
    
    
    if graph :
        plt.plot(lon, lat, '-', lonsmooth, latsmooth, '-') #, xp, p(xp), '-')
        filename = activity + '.png'
        plt.savefig(filename, facecolor = fig.get_facecolor(), bbox_inches='tight', pad_inches=0, dpi=900)

    return
