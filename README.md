# Python ArmarX - A Python toolbox for ArmarX

```
from armarx import 🤖  as ❤ 
```

This package provides Python 3 bindings for ArmarX.

In addition, the package also includes some helper functions, such as
publishing or subscribing to images.


## Installation

to use the armarx_control feature, you need the following packages at the moment, it will
be cleaner soon.
- This package in `armarx_control` branch
- `armarx/skills/control` package (`new_mp_controller_refactor` branch) is where the NJointControllers are implemented.
- `RobotControllers` package (`refactor` branch) contains the glue code, the `kvil` components, which helps you to create a controller and 
manipulate the controllers. It also provides you with functions to get pose from and set target to the robot.

---

`pip install --upgrade --extra-index-url https://pypi.humanoids.kit.edu/ armarx`

## Using the bindings

### Connecting to an existing proxy

For proxies defined in a project's `Variants-*.xml` it is possible to import
the interface directly. 

```python
from armarx import PlatformUnitInterfacePrx
platform_unit = PlatformUnitInterfacePrx.get_proxy('Armar6PlatformUnit')
platform_unit.moveTo(0.0, 0.0, 0.0, 50.0, 0.1)
```

Slice definitions can be loaded using the `slice_loader.load_armarx_slice`
function. Default values for the proxy name will also be mapped.

More examples can be found in the `examples` folder.

### Using the robot and armarx_control module

examples:
- see `armarx_control/robots/commom.py` for platform, hand and arm motion control, basic set up of robot configurations.
- see `robot-policy-learning` package for movement primitive controllers. 
  - task space impedance controller on both real and simulated robot: `robot-policy-learning/robot_policy/classical/real/taskspace_impedance_mp_controller.py`

## Documentation

See `https://armarx.humanoids.kit.edu/python`
