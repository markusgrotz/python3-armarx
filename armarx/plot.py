import numpy as np
from matplotlib.colors import ListedColormap


def kit_color_map():
    color_names = [ 'KIT-Grün exklusiv', 'Blau exklusiv', 'Maigrün', 'Gelb', 'Orange', 'Braun', 'Rot', 'Lila', 'Cyan-Blau']
    kit_colors = np.array([[0, 150, 130, 255],
    [70, 100, 170, 255],
    [140, 182, 60, 255],
    [252, 229, 0, 255],
    [223, 155, 27, 255],
    [167, 130, 46, 255],
    [162, 34, 35, 255],
    [163, 16, 124, 255],
    [35, 161, 224,  255]])
    kit_colors = kit_colors / 255
    return ListedColormap(kit_colors[2:])
