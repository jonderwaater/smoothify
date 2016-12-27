# stravasmooth

#### Obtains a gpx file from your Strava activity and re-uploads after applying a smoothening algorithm.

If you suffer from jittery GPS data and from Strava consequently overestimating your athletic abilities (especially for runs), run this software for a more realistic account.

## Installation

````bash
pip install git+https://github.com/jonderwaater/stravasmooth  
````
You might have to install gpxpy separately (pip install git+https://github.com/tkrajina/gpxpy)

You need an access token. You can generate it on https://stravacli-dlenski.rhcloud.com/. Store the token in ~/.stravacli as described above the generated token.

## General usage
Run the software:
````bash
$ stravasmoothen
````
Your original activity will be replaced automatically. 

In the directory where you run stravasmoothen the following files are created:  
[Activity name].gpx           - the gpx file of your original activity  
[Activity name]_smooth.gpx    - the gpx file with smoothened data  
[Activity name].png           - plot comparing the original and the smoothened data  

Warning:  
This code has only been tested on activities recorded with the Strava Android App.  
Currently only position, time and elevation data are extracted, as well as the activity type, name and description.
That means: no heartrate data, kudos, comments, photos etc. This information from the Strava activity will be lost in the upload process unless you back it up by hand.

### Options
```
  -h        , --help                show this help message and exit
  -a <id>   , --activity-id <id>    activity id; latest activity is taken by default.
  -g        , --no-graph            do not create png file showing original and smoothened data.
  -u        , --no-upload           do not upload smoothened data to Strava.
  -d        , --dry-run             do not overwrite original activity when attempting to upload to Strava.
  -c        , --cleanup             delete created files after uploading activity.  
  -s <algo> , --algo <algo>         smoothening algorithm. running average (-s=1) is default.

```

### On Android
The program will also run on Android on the [Termux](https://play.google.com/store/apps/details?id=com.termux&hl=en) app. The installation method is identical to the one described above. Because of limited availability of packages it is required to run with option -g.

## The scripts

-- exportgpx.py  
Retrieves data from the latest Strava activity and writes it to a gpx file. As far as I know there is no other available method  to obtain a gpx file from the command line.  

-- smoothen.py  
Smoothens the data in the gpx file. Currently it uses a simple algorithm that takes running average of 9 points, in steps of 1 point. More advanced algorithms may be implemented in the future, but it's already a significant improvement over untreated data.

-- stravaup.py  
Uploads the the activity.  


## Dependencies
stravalib, matplotlib, gpxpy and others


OTHER SOURCES:  

Code has been shamelessly copied from  
https://github.com/dlenski/stravacli  
in order to download and upload Strava activities. Because of relatively large modifications I copied the code. I might prepare a pull request, and if accepted I'll refer to it as a true dependency.

Code presented in this [blog post](http://andykee.com/visualizing-strava-tracks-with-python.html) by Andy Kee is used to read and plot gpx files.



