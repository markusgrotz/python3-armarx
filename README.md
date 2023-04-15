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
- `armarx/skills/control` package (`new_mp_controller_refactor_jianfeng` branch) is where the NJointControllers are implemented.

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

Steps to check:
- To use it on the robot, you should make sure the above packages are compiled on the local machine where you run your 
Python applications.
- Start ArmarX on the control PC (armar6a-1) and start low/high-level scenarios. 
- Start the robot-unit, make sure the `armarx/skills/control` package is on branch `new_mp_controller_refactor_jianfeng` in your 
workspace on armar6a-0.
- Start the `controller_creator` component in the `ControlScenario` on armar6a-0. Note, the `ControlScenario` is in the `armarx_control` package.
- Run the demo script below. The robot will move back and forth, then close and open both hand, and then raise both arms straight up 300 mm, in
the meanwhile, the hands close gradually. This demonstrates how you can connect to the proxies on the robot and interact with them.
```shell
cd python3-armarx
python armarx_control/robots/common.py
```

MP controller example: the robot will move the arm with a straight line trajectory encoded as Via-point Movement Primitive (VMP). The target is 
30 cm above the current pose. You can, e.g., move the arm to `NavigationPose` before testing the following script.
```shell
cd python3-armarx
python armarx_control/test/ts_impedance_mp_controller.py
```

The above steps is temporal now, they will be simplified in the future.

examples:
- see `armarx_control/robots/commom.py` for platform, hand and arm motion control, basic set up of robot configurations.
- see the teleoperation control in `robot-utils/robot_utils/armar/teleoperation/holistic_teleop.py`
- see `robot-policy-learning` package for movement primitive controllers. 
  - task space impedance controller on both real and simulated robot: `robot-policy-learning/robot_policy/classical/real/taskspace_impedance_mp_controller.py`

## Documentation

See `https://armarx.humanoids.kit.edu/python`
