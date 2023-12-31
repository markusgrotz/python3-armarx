# Tutorial: Use `armarx_control`

[[_TOC_]]

---

to use the armarx_control feature, you need the following packages at the moment, it will
be cleaner soon.
- This package in `master` branch
- `armarx/skills/control` package (`main` branch) is where the NJointControllers are implemented.

## Using the Real Robot and `armarx_control` Module

### Example of using task space impedance controller:
1. Start ArmarX on the planning PC (e.g. `armar6a-1` on ARMAR-6) and start low/high-level scenarios. 
   ```shell
   # In a new terminal on armar6a-1
   armarx start
   armarx memory start
   armarx gui
   # In the GUI, start low/high-level scenario
   ```
2. To use the Python binding on the robot with the new controllers, you should make sure the `armarx/skills/control` 
   package is compiled on the control PC of the robot (e.g. `armar6a-0` on ARMAR-6). 
   
   If you do not have your own workspace, you can use the following workspace if you do not change anything
    ```shell
    # In a new terminal on armar6a-0
    axii w act your_workspace
    start_unit
    # In a new terminal on armar6a-0
    axii w act your_workspace
    armarx gui
    # In the pop up GUI, find the component `controller_creator` in the `ControlScenario` scenario.
    # start the component, make sure you see "controller_creator is ready" in the log
    # Note, the `ControlScenario` is in the `armarx_control` package.
    ```
3. Run the example demo script below. The robot will move back and forth, then close and open both hand, and then raise both arms straight up 300 mm, in
   the meanwhile, the hands close gradually. This demonstrates how you can connect to the proxies on the robot and interact with them.
    ```shell
    cd python3-armarx
    # create the bimanual impedance controller using configuration json file
    python armarx_control/run/bimanual_imp_ctrl.py
    # see command line args
    python armarx_control/run/bimanual_imp_ctrl.py -h
   
    # Python script read the configuration json and create the bimanual impedance controller using Aron
    python armarx_control/run/bimanual_imp_ctrl.py -a
    ```
   If you see hand not closed, this might due to the issue of hand unit, which has to be activated once.
4. Run unimanual example: default using left arm, to use right arm, specify `-r`.
   ```shell
   python armarx_control/run/uni_manual_imp_ctrl.py -a -r
   ```
5. MP controller example: the robot will move the arm with a straight line trajectory encoded as Via-point Movement Primitive (VMP). The target is 
   30 cm above the current pose. You can, e.g., move the arm to `NavigationPose` before testing the following script.
    ```shell
    cd python3-armarx
    python armarx_control/run/mp_forward_backward.py -f kinesthetic_teaching-2023-06-18-16-21-15 -t 5.0 -r -a
    # see help 
    python armarx_control/run/mp_forward_backward.py -h
    ```

More examples:
- see `armarx_control/robots/commom.py` for platform, hand and arm motion control, basic set up of robot configurations.
- see the teleoperation control in `robot-utils/robot_utils/armar/teleoperation/holistic_teleop.py`
- see `robot-policy-learning` package for movement primitive controllers. 
  - task space impedance controller on both real and simulated robot: `robot-policy-learning/robot_policy/classical/real/taskspace_impedance_mp_controller.py`


#### Examples of Using Cameras Only

If you only need the monocular or stereo cameras, then you do not need the `ControlScenario` 
which is in the `armarx_control` package.
Just do the following

```shell
from armarx_control.robots.common import Robot, cfg
robot_cfg = cfg.RobotConfig()
if cam_mode == "stereo":
    robot_cfg.stereo = cfg.StereoCameraConfig()
else:
    robot_cfg.mono = cfg.MonocularCameraConfig()
robot = Robot(robot_cfg)
if cam_mode == "stereo":
    images, info = robot.get_stereo_images()
    img = images[0]
else:
    img, depth, info = robot.get_mono_images(True)
```

You can find more examples of vision algorithms in the 
[`robot-vision` package]([https://git.h2t.iar.kit.edu/sw/machine-learning-control/robot-vision])
or contact jianfeng.gao@kit.edu for more details.
