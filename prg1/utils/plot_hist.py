import numpy as n
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from prg1.utils.cmap import discrete_cmap


def generate_plot(observation_list, bar_width=0.3, show_plot=True):
    """
    Generate Histogram for observation time
    """
    ax = plt.subplot(111)
    cmap = discrete_cmap(len(observation_list))

    bins = []
    names = []
    data = []
    l = []
    for i, obs in enumerate(observation_list):
        names.append(obs["name"])
        data.append(obs["duration"])
        bins.append((i + 1) - bar_width / 2)
        l.append(i)

    l = l[::-1]

    yticks = [25*(i+1) for i in range(9)]
    ax.set_yticks(yticks)  # Define the yticks
    ax.bar(bins, data, width=bar_width, color=cmap(l))    
    ax.set_xticks([x for x in range(len(observation_list)+1)])
    ax.set_xticklabels(names,rotation=45, rotation_mode="anchor", ha="right")
    ax.set_ylim(ymin=0, ymax=250)

    if show_plot:
        plt.show()
