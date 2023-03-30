import warnings

warnings.warn(
    "Use 'armarx_core.arviz.grids' instead.", DeprecationWarning
)

from armarx_core.arviz.grids.core import make_grid
from armarx_core.arviz.grids.spherical import make_spherical_grid, vis_sphere_mesh