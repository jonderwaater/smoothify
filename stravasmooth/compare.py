
import gpxpy
import gpxpy.geo as mod_geo



def comparefiles(gpxf1,gpxf2) :
    gpx_file1 = open(gpxf1, 'r')
    gpx_file2 = open(gpxf2, 'r')
    gpx1 = gpxpy.parse(gpxf1)
    gpx2 = gpxpy.parse(gpxf2)
    comparegpx(gpx1,gpx2,graph)



def comparegpx(gpx1,gpx2) :

    moving_time1, stopped_time1, moving_distance1, stopped_distance1, max_speed1 = gpx1.get_moving_data()
    moving_time2, stopped_time2, moving_distance2, stopped_distance2, max_speed2 = gpx2.get_moving_data()

    return moving_distance1,moving_distance2



def plot(outfile,gpx1,gpx2) :
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt


    lat = []
    lon = []
    latsmooth = []
    lonsmooth = []

    for track in gpx1.tracks:
        for segment in track.segments:
            for point in segment.points:
                lat.append(point.latitude)
                lon.append(point.longitude)


    for track in gpx2.tracks:
        for segment in track.segments:
            for point in segment.points:
                latsmooth.append(point.latitude)
                lonsmooth.append(point.longitude)


    fig = plt.figure(facecolor = '0.05')
    ax = plt.Axes(fig, [0., 0., 1., 1.], )
    ax.set_aspect('equal')
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.plot(lonsmooth, latsmooth, '-',zorder=1)
    plt.scatter(lon, lat, s=1, color='red', edgecolor='',zorder=2)
    plt.savefig(outfile, facecolor = fig.get_facecolor(), bbox_inches='tight', pad_inches=0, dpi=900)


