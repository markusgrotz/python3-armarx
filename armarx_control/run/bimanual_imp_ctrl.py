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


def run_bimanual_imp_ctrl(
        robot: Robot,
        config_filename: str = None,
        from_aron: bool = True,
):
    config = TaskspaceImpedanceControllerConfig().from_json(config_filename) if from_aron else config_filename

    control_type = ControllerType.TSImpedance
    nodeset_left = Armar6NodeSet.LeftArm
    nodeset_right = Armar6NodeSet.RightArm
    tcp_left = Armar6TCP.LeftArm
    tcp_right = Armar6TCP.RightArm

    controller_name, ctrl, _cfg = robot.create_controller(
        "python_bi_imp", control_type, config, True, True
    )

    try:
        _cfg: TaskspaceImpedanceControllerConfig
        init_target_pose_l = _cfg.cfg.get(nodeset_left.value).get_desired_pose()
        init_target_pose_r = _cfg.cfg.get(nodeset_right.value).get_desired_pose()
        ic(init_target_pose_l)
        ic(init_target_pose_r)
        input("continue ... ")

        console.log("close hands")
        robot.close_hand(cfg.Side.left, 1.0, 1.0)
        robot.close_hand(cfg.Side.right, 1.0, 1.0)
        time.sleep(1)
        console.log("open hands")
        robot.close_hand(cfg.Side.left, 0, 0)
        robot.close_hand(cfg.Side.right, 0, 0)
        time.sleep(1)

        target_left = copy.deepcopy(init_target_pose_l)
        target_right = copy.deepcopy(init_target_pose_r)
        console.log(f"Initial target, left: \n{target_left}\nand right: \n{target_right}")
        console.log(
            f"current_pose, left: \n{robot.get_pose(tcp_left.value)} \nand right: \n{robot.get_pose(tcp_right.value)}")

        n_steps = 200
        pose_z_range_left = np.linspace(target_left[2, 3], target_left[2, 3] + 100.0, n_steps)
        pose_z_range_right = np.linspace(target_right[2, 3], target_right[2, 3] + 100.0, n_steps)
        finger_range_left = np.linspace(0, 1, n_steps)
        finger_range_right = np.linspace(0, 1, n_steps)
        t = 0
        dt = 0.01
        for i in range(n_steps):
            target_left[2, 3] = pose_z_range_left[i]
            target_right[2, 3] = pose_z_range_right[i]
            robot.close_hand(cfg.Side.left, finger_range_left[i], finger_range_left[i])
            robot.close_hand(cfg.Side.right, finger_range_right[i], finger_range_right[i])

            config: TaskspaceImpedanceControllerConfig = robot.get_controller_config(controller_name)
            config.cfg.get(nodeset_left.value).set_desired_pose(target_left)
            config.cfg.get(nodeset_right.value).set_desired_pose(target_right)
            robot.update_controller_config(controller_name, config)

            time.sleep(dt)
            t += dt

        config: TaskspaceImpedanceControllerConfig = robot.get_controller_config(controller_name)

        console.log(f"current_pose, left: \n{robot.get_pose(tcp_left.value)} \n"
                    f"and right: \n{robot.get_pose(tcp_right.value)}")
        console.log(f"target pose : left: \n{config.cfg.get(nodeset_left.value).get_desired_pose()} \n"
                    f"and right: \n{config.cfg.get(nodeset_right.value).get_desired_pose()}")

    except RuntimeError as e:
        console.log(f"error: {e}")
    finally:
        robot.close_hand(cfg.Side.left, 0, 0)
        robot.close_hand(cfg.Side.right, 0, 0)
        robot.delete_controller(controller_name)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("--from_aron", "-a", is_flag=True, help="to create controller from aron config")
def main(from_aron: bool):
    np.set_printoptions(suppress=True, precision=3)
    robot = get_control_robot()

    from armarx_control.utils.pkg import get_armarx_package_data_dir

    p = get_armarx_package_data_dir("armarx_control")
    p = p / "controller_config/NJointTaskspaceImpedanceController/default.json"
    if not p.is_file():
        raise FileExistsError(f"{p} does not exist")
    run_bimanual_imp_ctrl(robot, str(p), from_aron)


if __name__ == "__main__":
    main()
