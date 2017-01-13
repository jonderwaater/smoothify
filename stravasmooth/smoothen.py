import re
import fileinput
import sys
import tempfile
import time
import multiprocessing as mp
from gpxpy import geo as mod_geo
from . import functions
from datetime import datetime
import copy

def getgpxstring(filename,algo=1):
    with open(filename, 'r') as f:
      gpx_file_data=f.read()
    return gpx_file_data

def smoothengpxfilename(filename, algo=1) :
    with open(filename, 'r') as f:
      gpxdata=f.read()
    gpxdata_smooth,lat,lon,ele,latsmooth,lonsmooth,elesmooth = smoothengpx(gpxdata,algo)
    return gpxdata_smooth,lat,lon,ele,latsmooth,lonsmooth,elesmooth

def smoothengpx(gpx_file_smooth_data, algo, return_dict=None) :
    
    infile = tempfile.NamedTemporaryFile('w',1)
    infile.write(gpx_file_smooth_data)
    tempfilename = infile.name

    tempf = open(tempfilename, 'r')
    temp = tempf.read()

    lat,lon,ele,times = functions.getarraysfile(gpx_file_smooth_data)

    latsmooth = list(lat)
    lonsmooth = list(lon)
    elesmooth = list(ele)
    
    # this is the smoothening algorithm
    nsection=7
    for sectionstart in range(0,len(lon)-1-nsection):
        centslice = int(sectionstart+(nsection-1)/2)
        lonslice = lon[sectionstart:sectionstart+nsection]
        latslice = lat[sectionstart:sectionstart+nsection]
        eleslice = ele[sectionstart:sectionstart+nsection]
        timesslice = times[sectionstart:sectionstart+nsection]

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
            elesmooth[centslice] = sum(eleslice)/len(eleslice)
        
        # time limit on point average
        if int(algo) == 2 :
            midstamp = datetime.strptime(timesslice[(nsection-1)/2], "%Y-%m-%dT%H:%M:%SZ")
            i=-1
            while i < len(latslice)-1 :
                i = i+1
                thisstamp  = datetime.strptime(timesslice[i], "%Y-%m-%dT%H:%M:%SZ")
                delta = thisstamp - midstamp
                delta = abs(delta)
                if delta.seconds > 6 :
                    latslice = latslice[:i] + latslice[i+1 :]
                    lonslice = lonslice[:i] + lonslice[i+1 :]
                    eleslice = eleslice[:i] + eleslice[i+1 :]
                    timesslice = timesslice[:i] + timesslice[i+1 :]
                    i = i-1

            lonsmooth[centslice] = sum(lonslice)/len(lonslice)
            latsmooth[centslice] = sum(latslice)/len(latslice)
            elesmooth[centslice] = sum(eleslice)/len(eleslice)


    distance=0
    pos=0
    i=-1
    while i < len(lat)-1 :
        i = i + 1
        tempf.seek(pos)
        line = tempf.readline()
        pos = tempf.tell()
        line = line + tempf.readline()
        linevalues = re.findall("\d+\.\d+",line)
        if(len(linevalues)==3):
            thislat = float(linevalues[0])
            thislon = float(linevalues[1])

            newline = '   <trkpt lat="{0:.7f}" lon="{1:.7f}">\n    <ele>{2:.1f}</ele>\n'.format(latsmooth[i],lonsmooth[i],elesmooth[i])
            gpx_file_smooth_data = gpx_file_smooth_data.replace(line,newline)

        else :
            i = i -1


         #   print(line,thislat,thislon)
    
         #   if thislat == lat[i]:
         #       if thislon == lon[i]:
         #           if i > 0 :
         #               distance = distance + mod_geo.distance(latsmooth[i],lonsmooth[i],elesmooth[i],latsmooth[i-1],lonsmooth[i-1],elesmooth[i-1])
    
         #           newline = '   <trkpt lat="{0:.7f}" lon="{1:.7f}">\n    <ele>{2:.1f}</ele>\n'.format(latsmooth[i],lonsmooth[i],elesmooth[i])
         #           #newline = '   <trkpt lat="{0:.7f}" lon="{1:.7f}">\n    <ele>{2:.1f}</ele>\n    <extensions>\n      <distance>{3:.2f}</distance>\n    </extensions>\n'.format(latsmooth[i],lonsmooth[i],elesmooth[i],distance)
         #           gpx_file_smooth_data = gpx_file_smooth_data.replace(line,newline)
         #           break

    if return_dict == None :
        return gpx_file_smooth_data,lat,lon,ele,latsmooth,lonsmooth,elesmooth

    return_dict[0] = gpx_file_smooth_data
    return_dict[1] = lat
    return_dict[2] = lon
    return_dict[3] = ele
    return_dict[4] = latsmooth
    return_dict[5] = lonsmooth
    return_dict[6] = elesmooth



def runsmoothengpx(args) :
    manager = mp.Manager()
    return_dict = manager.dict()
    if len(args) == 1 :
        args = args + (1,)
    args = args + (return_dict,)
    proc=mp.Process(target=smoothengpx,args=args)
    #proc.daemon=True
    proc.start()
    proc.join()
    return return_dict.values()[0],return_dict.values()[1],return_dict.values()[2],return_dict.values()[3],return_dict.values()[4],return_dict.values()[5],return_dict.values()[6]

                            

def writeoutput(filename,gpx) :
    print('File created: {}'.format(filename))
    with open(filename, 'w') as file :
        file.write(gpx)


def main(filename,algo=1):
    gpxsmooth,lat,lon,ele,latsmooth,lonsmooth,elesmooth = smoothengpxfilename(filename,algo)
    newfilename = filename.replace('.gpx','_smooth.gpx')
    writeoutput(newfilename,gpxsmooth)
    return gpxsmooth,lat,lon,ele,latsmooth,lonsmooth,elesmooth


if __name__ == "__main__":

    filename = sys.argv[1]

    if len(sys.argv) > 1 :
        algo = 1
        if len(sys.argv) > 2 :
            algo = sys.argv[2]

    main(filename, algo)


