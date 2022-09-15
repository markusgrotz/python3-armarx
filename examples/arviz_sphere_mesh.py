#!/usr/bin/env python3

import numpy as np

import armarx.arviz as viz
from armarx.arviz import grids


def vis_blue_sphere(alpha=255):
    return grids.vis_sphere_mesh(name="Blue", color=(0, 0, 255, alpha))


def vis_colored_sphere():
    mesh = grids.vis_sphere_mesh(
        name="z-colored", spherical_color_fn=lambda xs: xs[..., 1] + 2 * xs[..., 2]
    )
    mesh.position = (3, 0, 0)
    return mesh


def vis_deformed_sphere():
    grid = grids.make_spherical_grid(num=(65, 33), radius=1)

    # Change radius.
    def radius(spherical: np.ndarray) -> np.ndarray:
        azim = spherical[..., 1]
        elev = spherical[..., 2]
        return 1 + np.sin(azim) + np.cos(elev)

    grid[..., 0] = radius(grid)

    mesh = grids.vis_sphere_mesh(
        name="deformed", color=(0, 128, 255), grid_spherical=grid
    )
    mesh.position = (8, 0, 0)
    return mesh


def main():
    # Create a client with a name.
    arviz = viz.Client("ArViz Sphere Mesh Python Example")

    with arviz.begin_stage(commit_on_exit=True) as stage:

        layer_blue = stage.layer("blue")
        layer_blue.add(vis_blue_sphere(alpha=128))

        layer_colored = stage.layer("colored")
        layer_colored.add(vis_colored_sphere())

        layer_deformed = stage.layer("deformed")
        layer_deformed.add(vis_deformed_sphere())


if __name__ == "__main__":
    main()
