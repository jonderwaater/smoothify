#!/usr/bin/env python2
import extractgpx
import smoothen
import stravaup
import ConfigParser
import argparse
from sys import stderr, stdin

p = argparse.ArgumentParser(description='''Smoothen last activity on Strava.''')
p.add_argument('activities', nargs='*', type=argparse.FileType("rb"), default=(stdin,),
                   help="Export gpx, smoothen data, and upload activity")
p.add_argument('-g', '--graph'    , action='store_true', help="Do not create png file showing original and smoothened data.")
p.add_argument('-u', '--no-upload', action='store_true', help="Do not upload smoothened data to Strava.")
p.add_argument('-d', '--dry-run'  , action='store_true', help="Do not overwrite original activity when attempting to upload to Strava.")

args = p.parse_args()

filename = extractgpx.main()
smoothen.smoothen(filename,args.graph)
options = "-P"
if not args.dry_run :
    options = options + " -o"
if not args.no_upload :
    stravaup.main(options+" "+filename+"_smooth.gpx")
