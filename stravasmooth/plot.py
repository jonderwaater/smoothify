
import matplotlib.pyplot as plt

def plot(activity,lon,lat,lonsmooth,latsmooth) :
    fig = plt.figure(facecolor = '0.05')
    ax = plt.Axes(fig, [0., 0., 1., 1.], )
    ax.set_aspect('equal')
    ax.set_axis_off()
    fig.add_axes(ax)
    #plt.plot(lonsmooth, latsmooth, '-', lon, lat, '.') #, xp, p(xp), '-')
    plt.plot(lonsmooth, latsmooth, '-',zorder=1) #, xp, p(xp), '-')
    plt.scatter(lon, lat, s=1, color='red', edgecolor='',zorder=2) #, xp, p(xp), '-')
    filename = activity + '.png'
    plt.savefig(filename, facecolor = fig.get_facecolor(), bbox_inches='tight', pad_inches=0, dpi=900)

