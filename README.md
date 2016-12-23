# strava-smooth

## INTRODUCTION

Export data from the last Strava activity to a gpx file, smoothen the GPS data, and re-upload the activity.

Functionality of the scripts:

-- strava-smooth.py  
Runs the job as described above.

-- exportgpx.py  
Retrieves data from the last Strava activity and writes it to a gpx file.  
**Warning**:  
  This code has only been tested on activities recorded with the Strava Android App.  
  Currently only position, time and elevation data are extracted.  
  That means: no heartrate data, no kudos, no comments etc. This information from the Strava activity will be lost in the upload process unless you back it up by hand.

-- smoothen.py  
Smoothens the data in the gpx file. Currently it uses a simple algorithm written by myself that interpolates between sets of 9 points. More advanced algorithms may be implemented in the future, but it's already a significant improvement over untreated data.

-- stravaup.py  
Uploads the the activity.  
**Warning**:  
  In order to upload the new data to Strava, the old activity (duplicate) has to be deleted. You may loose data, so make backups if you are not sure.


## DEPENDENCIES

The code requires libraries from  
https://github.com/hozn/stravalib  
https://github.com/tkrajina/gpxpy  
For installation directions I refer to the respective repositories.  
Gpxpy is used to play with gpx coordinates. Stravalib is used to communicate with the Strava API.

You need an access token. You can generate it on https://stravacli-dlenski.rhcloud.com/. The code expects the token to be saved according to the instructions on that page.


OTHER SOURCES:  

Code has been shamelessly copied from  
https://github.com/dlenski/stravacli  
in order to download and upload Strava activities. Because of relatively large modifications I copied the code. I might prepare a pull request, and if accepted I'll refer to it as a true dependency.

Code presented in this [blog post](http://andykee.com/visualizing-strava-tracks-with-python.html) by Andy Kee is used to read and plot gpx files.



