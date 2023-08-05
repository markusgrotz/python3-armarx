import time
import copy
import click
import numpy as np

from armarx_control import console
from armarx_control.config.common import ControllerType
from armarx_control.robots.common import cfg, Robot
from armarx_control.config.njoint_controllers.taskspace_impedance import TaskspaceImpedanceControllerConfig
from armarx_control.config.robots.armar6 import Armar6TCP, Armar6NodeSet


def get_control_robot():
    c = cfg.RobotConfig()
    c.robot_unit = cfg.RobotUnitConfig()
    c.kinematic_unit = cfg.KinematicUnitConfig()
    c.ctrl = cfg.ControllerCreatorConfig()
    c.hand = cfg.HandUnitConfig()
    c.platform = cfg.PlatformUnitConfig()
    return Robot(c)


def run_uni_manual_imp_ctrl(
        robot: Robot,
        config_filename: str = None,
        from_aron: bool = True,
        right_arm: bool = True,
):
    config = TaskspaceImpedanceControllerConfig().from_json(config_filename) if from_aron else config_filename

    control_type = ControllerType.TSImpedance
    nodeset = Armar6NodeSet.RightArm if right_arm else Armar6NodeSet.LeftArm
    tcp = Armar6TCP.RightArm if right_arm else Armar6TCP.LeftArm
    side = cfg.Side.right if right_arm else cfg.Side.left

    controller_name, ctrl, _cfg = robot.create_controller(
        "python_bi_imp", control_type, config, True, True
    )

    try:
        _cfg: TaskspaceImpedanceControllerConfig
        init_target_pose = _cfg.cfg.get(nodeset.value).get_desired_pose()
        ic(init_target_pose)
        input("continue ... ")

        console.log("close hands")
        robot.close_hand(side, 1.0, 1.0)
        time.sleep(1)
        console.log("open hands")
        robot.close_hand(side, 0, 0)
        time.sleep(1)

        target = copy.deepcopy(init_target_pose)
        console.log(f"Initial target: \n{target}")
        console.log(f"current_pose: \n{robot.get_pose(tcp.value)}")

        n_steps = 200
        pose_z_range = np.linspace(target[2, 3], target[2, 3] + 100.0, n_steps)
        finger_range = np.linspace(0, 1, n_steps)
        t = 0
        dt = 0.01
        for i in range(n_steps):
            target[2, 3] = pose_z_range[i]
            robot.close_hand(side, finger_range[i], finger_range[i])

            config: TaskspaceImpedanceControllerConfig = robot.get_controller_config(controller_name)
            config.cfg.get(nodeset.value).set_desired_pose(target)
            robot.update_controller_config(controller_name, config)

            time.sleep(dt)
            t += dt

        config: TaskspaceImpedanceControllerConfig = robot.get_controller_config(controller_name)

        console.log(f"current_pose: \n{robot.get_pose(tcp.value)}")
        console.log(f"target pose: \n{config.cfg.get(nodeset.value).get_desired_pose()}")

    except RuntimeError as e:
        console.log(f"error: {e}")
    finally:
        robot.close_hand(side, 0, 0)
        robot.delete_controller(controller_name)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("--from_aron", "-a", is_flag=True, help="to create controller from aron config")
@click.option("--right_arm", "-r", is_flag=True, help="set to use right arm, otherwise left arm")
def main(from_aron: bool, right_arm: bool):
    np.set_printoptions(suppress=True, precision=3)
    robot = get_control_robot()

    from armarx_control.utils.pkg import get_armarx_package_data_dir

    side = "right" if right_arm else "left"
    p = get_armarx_package_data_dir("armarx_control")
    p = p / f"controller_config/NJointTaskspaceImpedanceController/default_{side}.json"
    ic(p)
    if not p.is_file():
        raise FileExistsError(f"{p} does not exist")
    run_uni_manual_imp_ctrl(robot, str(p), from_aron, right_arm)


if __name__ == "__main__":
    main()


# NOTE: python
