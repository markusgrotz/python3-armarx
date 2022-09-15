import numpy as np

from typing import Callable, Optional, Tuple, Union

from .core import make_grid


def make_spherical_grid(
    num: Union[int, Tuple[int, int]] = (50, 50),
    radius: Optional[float] = None,
) -> np.ndarray:
    """
    Make a grid of spherical coordinates (azim, elev) spanning
    [-pi, pi] x [-pi/2, pi/2].
    :param num:
        The number of samples along each dimension.
        (n_azim, n_elev) or (n) if n_azim == n_elev = n.
    :param radius:
        If specified, a constant radius dimension will be prepended
        to (azim, elev), i.e. each coordinate will be (radius, azim_i, elev_j).
    :return:
        If no radius is specified, a grid of spherical coordinates (azim, elev)
        of shape (n_azim, n_elev, 2).
        If a radius is specified, a grid of spherical coordinates (radius, azim, elev)
        of shape (n_azim, n_elev, 3).
    """
    try:
        num_azim, num_elev = num
    except TypeError:
        num_azim, num_elev = num, num

    azim_lim = (-np.pi, np.pi)
    elev_lim = (-np.pi / 2, np.pi / 2)
    azims = np.linspace(*azim_lim, num_azim)
    elevs = np.linspace(*elev_lim, num_elev)

    grid = make_grid(azims, elevs)

    if radius is not None:
        grid = np.insert(grid, 0, radius, axis=-1)

    return grid


def vis_sphere_mesh(
    name: str,
    num: Union[int, Tuple[int, int]] = (65, 33),
    radius=1.0,
    grid_spherical: Optional[np.ndarray] = None,
    color=(196, 196, 196, 255),
    spherical_color_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    cmap: Union[str, Callable] = "viridis",
) -> "armarx.arviz.Mesh":
    """
    Create a colored sphere mesh.
    :param name:
        The name of the mesh element.

    :param num:
        If `grid_spherical` is None, the number of vertices for azimuth and elevation.
    :param radius:
        If `grid_spherical` is None, the sphere's constant radius.
    :param grid_spherical:
        If specified, the grid of spherical coordinates of shape (..., 3)
        with entries (radius, azimuth, elevation).
        If not specified, it is constructed based on the arguments `num`
        and `radius`.
        This an also be used to draw shapes with non-constant radius.

    :param color:
        If `spherical_color_fn` is None, a constant color for all vertices.
    :param spherical_color_fn:
        If specified, determines the color of each vertex together with cmap.
        The function is passed the spherical coordinates of all vertices in a
        (N, 3) array and should return a scalar value y for each coordinate,
        which is passed through cmap to obtain the color of the vertex.
        The colormap is normalized to (0, y_max).
    :param cmap:
        The colormap which is used together with spherical_color_fn to
        determine vertex colors.

    :return:
        The sphere mesh.
    """
    from armarx.math import spherical
    from armarx import arviz as viz

    if grid_spherical is None:
        grid_spherical = make_spherical_grid(num=num, radius=radius)
    grid_cartesian = spherical.spherical2cartesian(grid_spherical)
    grid_cartesian = grid_cartesian.reshape((-1, 3), order="F")

    if spherical_color_fn is None:
        color = np.array(color)
        if color.shape == (3,):
            colors = np.zeros_like(grid_cartesian, dtype=int)
        elif color.shape == (4,):
            colors = np.insert(np.zeros_like(grid_cartesian, dtype=int), 0, 0, axis=-1)
        else:
            raise ValueError(
                f"Expected color to have shape (3,) or (4,), but got {color.shape}."
            )
        colors[:] = color

    else:
        from matplotlib import cm
        from matplotlib.colors import Normalize

        cmap: Callable
        if isinstance(cmap, str):
            cmap = cm.get_cmap(cmap)

        grid_spherical = grid_spherical.reshape((-1, 3), order="F")
        ys = spherical_color_fn(grid_spherical)

        colors = cmap(Normalize(vmin=0, vmax=np.max(ys))(ys))
        colors = (colors * 255).astype(int)

    mesh = viz.Mesh(name)
    mesh.vertices = grid_cartesian
    mesh.colors = colors
    mesh.faces = viz.Mesh.make_grid2d_faces(*num)

    return mesh
