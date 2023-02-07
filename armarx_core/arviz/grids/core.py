import numpy as np


def make_grid(
    *x_i,
) -> np.ndarray:
    """
    Given arrays N arrays
        (a_i) (i=1..M_a), (b_j) (j=1..M_b), ..., (z_k) (k = 1..M_z),
    where each array is a 1D array containing M_* points along a dimension,
    construct a grid containing all combinations (a_i, b_j, ..., z_k) in R^N
    structured in an (N+1) dimensional array of shape (M_a, M_b, ..., M_z, N).

    For example::

        a = np.arange(4)  # shape (4,)
        b = np.arange(5)  # shape (5,)
        c = np.arange(6)  # shape (6,)
        grid = make_grid(a, b, c)  # shape (4, 5, 6, 3)
        point = grid[0, 3, 5]  # shape (3,)
        print(point)  # array([0 3 5])

    :param x_i: Arrays specifying the points along each dimension.
    :return: A grid of coordinates.
    """
    return np.moveaxis(np.stack(np.meshgrid(*x_i, indexing="ij")), 0, -1)
