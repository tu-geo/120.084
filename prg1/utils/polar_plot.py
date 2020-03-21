import numpy as np
import matplotlib.pyplot as plt


def generate_plot(orbit_list, show_plot=True):
    ax = plt.subplot(111, projection="polar")
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    #ax.set_yticks(range              (0, 90, 10))    # (min int, max int, increment) 
    #ax.set_yticklabels(map(str, range(90, 0, -10)))
    rmax = 90
    ax.set_rmax(rmax)

    ticks = 6
    ticksize = int(rmax / ticks)
    tick_list = range(0, rmax + ticksize, ticksize)
    ax.set_yticks(tick_list)  # Define the yticks

    for orbit in orbit_list:
        ax.plot(orbit.get_azimuth_radian_array(), orbit.get_elevation_polar_array(), label=orbit.satellite_id)

    tick_labels = []
    for i, t in enumerate(tick_list):
        if t == 0 or t % ticksize == 0:
            tick_labels.append("{}".format(t))
        else:
            tick_labels.append("")
    chartBox = ax.get_position()
    ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.8, chartBox.height])
    ax.legend(loc='upper center', bbox_to_anchor=(1.45, 1.0), shadow=True, ncol=1)

    ax.set_yticklabels(tick_labels[::-1])

    if show_plot:
        plt.show()
