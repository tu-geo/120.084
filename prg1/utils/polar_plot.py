import numpy as np
import matplotlib.pyplot as plt


def generate_plot(orbit_list, show_plot=True):
    ax = plt.subplot(111, projection="polar")
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    rmax = 90
    ticks = 6
    ticksize = int(rmax / ticks)
    tick_list = range(0, rmax + ticksize, ticksize)

    for orbit in orbit_list:
        ax.plot(orbit.get_azimuth_radian_array(), orbit.get_elevation_polar_array(), label=orbit.satellite_id)

    ax.set_rmax(rmax)
    ax.legend()
    ax.set_yticks(tick_list)  # Define the yticks
    tick_labels = []
    for i, t in enumerate(tick_list):
        if t == 0 or t % ticksize == 0:
            tick_labels.append("{}".format(t))
        else:
            tick_labels.append("")
    ax.set_yticklabels(tick_labels[::-1])

    if show_plot:
        plt.show()
