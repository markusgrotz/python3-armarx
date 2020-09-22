# Python 3.0 bindings for ArmarX

This package provides Python 3.0 bindings for ArmarX.

In addition, the package also includes some helper functions, such as
publishing or subscribing to images.


## Installation

`pip3 install --user --upgrade --extra-index-url https://pypi.humanoids.kit.edu:443/ armarx-dev`

## Using the bindings

### Connecting to a proxy

For proxies defined in a `Variants-*.xml` it is possible to import the
interface directly. 

```python
from armarx import PlatformUnitInterfacePrx
platform_unit = PlatformUnitInterfacePrx.get_proxy('Armar6PlatformUnit')
platform_unit.moveTo(0.0, 0.0, 0.0, 50.0, 0.1)
```

Slice definitions can be loaded using the `slice_loader.load_armarx_slice`
function. Default values for the proxy name will also be mapped.


More examples can be found in the `examples` folder.


