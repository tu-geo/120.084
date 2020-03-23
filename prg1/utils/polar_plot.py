import numpy as np
import matplotlib.pyplot as plt


def generate_plot(orbit_list, show_plot=True):
    """
    Generate Skyplot
    """
    ax = plt.subplot(111, projection="polar")
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    rmax = 90

    ticks = 6
    ticksize = int(rmax / ticks)
    ax.set_yticks(range(0, rmax + ticksize, ticksize))  # Define the yticks
    ax.set_yticklabels(map(str, range(rmax, 0, -ticksize)))

    for orbit in orbit_list:
        ax.scatter(orbit.get_azimuth_radian_array(), orbit.get_elevation_polar_array(), s=1, label=orbit.satellite_id)

    # Put Legend to correct position
    chartBox = ax.get_position()
    ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.8, chartBox.height])
    ax.legend(loc='upper center', bbox_to_anchor=(1.45, 1.0), shadow=True, ncol=1)

    ax.set_rmax(rmax / 1.0)
    ax.set_rmin(0.0)

    if show_plot:
        plt.show()
