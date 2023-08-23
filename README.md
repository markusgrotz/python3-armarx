# Python ArmarX - A Python Toolbox for ArmarX

This package provides Python 3 bindings for ArmarX,
including client classes for common interfaces.

[[_TOC_]]

---

## Installation

### Using Axii

Add and upgrade the module `armarx/python3-armarx` in Axii.

**Note:** The module is also included in the `armarx` module,
which is added to new workspaces by default.

```shell
axii workspace add armarx/python3-armarx
axii workspace upgrade -m armarx/python3-armarx
```


### From Source Using Pip

To install the ArmarX Python bindings into your virtual environment:

```shell
source .venv/bin/activate
# armarx__python3_armarx__PATH = Path to python3-armarx
pip install -e $armarx__python3_armarx__PATH
```

The `-e` flag is optional. 
If you pass the `-e` flag to pip, it will install the package in _editable_ mode,
which means that you do not have to reinstall the package if you update or change
the ArmarX python bindings.


## Usage

### Connecting to an Existing Proxy

Slice definitions can be loaded using the `slice_loader.load_armarx_slice()` function. 
Default values for the proxy name will also be mapped.

For proxies defined in a project's `Variants-*.xml` it is possible to import
the interface directly. 

```python
from armarx import PlatformUnitInterfacePrx
platform_unit = PlatformUnitInterfacePrx.get_proxy('Armar6PlatformUnit')
platform_unit.moveTo(0.0, 0.0, 0.0, 50.0, 0.1)
```


### Examples

More examples can be found in the [`examples`](examples) folder.
See also the [Examples in the ArmarX Academy](https://git.h2t.iar.kit.edu/sw/armarx/meta/academy/-/blob/main/examples/README.md).


### Use armarx_control

See [tutorial](docs/_tutorial_armarx_control.md)


## Documentation

See the [ArmarX API documentation](https://armarx.humanoids.kit.edu/python).
