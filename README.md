# Python 3.0 bindings for ArmarX

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


