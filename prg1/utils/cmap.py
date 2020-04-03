from matplotlib import cm
#import numpy as np


def discrete_cmap(N, reverse=False):
    """Create an N-bin discrete colormap from the specified input map"""

    # Note that if base_cmap is a string or None, you can simply do
    #    return plt.cm.get_cmap(base_cmap, N)
    # The following works for string, None, or a colormap instance:

    # base = cm.get_cmap(base_cmap)
    # color_list = base(np.linspace(0, 1, N))
    # cmap_name = base.name + str(N)
    #return base.from_list(cmap_name, color_list, N)
    map_name = "jet"
    if reverse:
        map_name += "_r"
    return cm.get_cmap(map_name, N)
