import matplotlib.pyplot as plt
import matplotlib.dates as md

import datetime
import numpy as np


def generate_plot(window_list, show_plot=True):

    fig, ax = plt.subplots()

    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%dT%H:%M:%S')

    y_tick_labels = []
    y_ticks = []

    bar_height = 8
    bar_space = 1

    bar_dist = bar_height + bar_space

    for i, sat in enumerate(window_list):
        y_tick_labels.append(sat["satellite"])
        ax.broken_barh([(t[0], t[1] - t[0]) for t in sat["windows"]], ((i + 1) * (bar_dist), bar_height))
        y_ticks.append((i + 1) * bar_dist)
        
    ax.grid(True)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_tick_labels)
    plt.xticks( rotation=25 )
    ax.xaxis.set_major_formatter(xfmt)

    if show_plot:
        plt.show()
