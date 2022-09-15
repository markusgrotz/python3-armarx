import numpy as np


def kit_colors():
    """

    https://intranet.kit.edu/gestaltungsrichtlinien.php
    """
    color_names = [
        "Grün",
        "Blau",
        "Gelb",
        "Orange",
        "Maigrün",
        "Rot",
        "Lila",
        "Braun",
        "Cyan",
    ]
    kit_colors = np.array(
        [
            [0, 150, 130, 255],
            [70, 100, 170, 255],
            [252, 229, 0, 255],
            [223, 155, 27, 255],
            [140, 182, 60, 255],
            [162, 34, 35, 255],
            [163, 16, 124, 255],
            [167, 130, 46, 255],
            [35, 161, 224, 255],
        ]
    )
    kit_colors = kit_colors / 255
    return zip(color_names, kit_colors)


def kit_color_map():
    from matplotlib.colors import ListedColormap

    return ListedColormap(kit_colors)
