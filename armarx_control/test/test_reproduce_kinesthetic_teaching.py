import time
import json
import click
import numpy as np
from pathlib import Path

from armarx_control import console
from armarx_control.robots.common import cfg, Robot, pose_to_vec
from armarx_control.utils.pkg import get_armarx_package_data_dir
from armarx_control.utils.file import copy_file_to_robot
from armarx_control.config.mp.mp_config import MPListConfig

from robot_utils.py.utils import load_dict_from_yaml, save_to_yaml
from robot_utils.py.filesystem import validate_file
from robot_utils.py.interact import ask_list


def run_ts_imp_mp_controller(
        robot: Robot,
        config_filename: Path,
        duration: float = 5.0,
        flag_delete_controller: bool = True,
        mp_config: MPListConfig = None
):
    control_type = "TSImpedanceMP"
    rns_right = "RightArm"
    tcp_right = "Hand R TCP"
    target_pose = []
    validate_file(config_filename, throw_error=True)

    controller_name, ctrl, cfg = robot.create_controller(
        "kvil_deploy", rns_right, control_type, str(config_filename), True
    )

    try:
        current_pose_r = pose_to_vec(robot.get_prev_target(controller_name))
        ctrl.updateMPConfig(mp_config.to_aron_ice())
        ctrl.learnFromCSV([])
        console.log(f"[bold cyan]Start with current pose: \n{current_pose_r}, target pose: \n{target_pose}")
        input("continue? ... ")
        ctrl.start("default", current_pose_r, target_pose, duration)

        _start = time.time()
        ready_to_stop = False
        while True:
            time.sleep(0.001)
            if ctrl.isFinished("default") and not ready_to_stop:
                _start = time.time()
                console.log("[bold green]VMP controller finished")
                ready_to_stop = True

            if ready_to_stop and (time.time() - _start) > 1.5:
                console.log("[bold green]stop impedance controller")
                break

        console.log(f"current_pose right: \n{robot.get_pose(tcp_right)}")
        console.log(f"target pose right: \n{robot.get_prev_target(controller_name)}")

    except RuntimeError as e:
        console.log(f"error: {e}")
    finally:
        if flag_delete_controller:
            robot.delete_controller(controller_name)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("--filename",     "-f",   type=str,      help="filename of the recorded traj (before -forward/-backward")
def main(filename):
    controller_type = "NJointTSImpedanceMPController"
    pkg_path = get_armarx_package_data_dir("armarx_control")
    config_file = pkg_path / f"controller_config/{controller_type}/default.json"
    mp_config_file = pkg_path / f"controller_config/{controller_type}/default_mp.json"
    validate_file(config_file, throw_error=True)
    validate_file(mp_config_file, throw_error=True)

    mp_cfg = MPListConfig().from_json(str(mp_config_file))
    ic(mp_cfg)

    c = cfg.RobotConfig()
    c.robot_unit = cfg.RobotUnitConfig()
    c.kinematic_unit = cfg.KinematicUnitConfig()
    c.ctrl = cfg.ControllerCreatorConfig()
    c.hand = cfg.HandUnitConfig()
    c.platform = cfg.PlatformUnitConfig()
    robot = Robot(c)

    def move_backward(mp_config: MPListConfig):
        motion_list = [str("/home/armar-user/armar6_motion/kinesthetic_teaching/" + f"{filename}-backward.csv")]
        mp_config.mp_list[0].file_list = motion_list
        ic(mp_config)
        if ask_list("return in a reversed way? ", ["yes", "no"]) == "yes":
            run_ts_imp_mp_controller(robot, config_file,
                                     duration=10, mp_config=mp_config)

    def move_forward(mp_config: MPListConfig):
        motion_list = [str("/home/armar-user/armar6_motion/kinesthetic_teaching/" + f"{filename}-forward.csv")]
        mp_config.mp_list[0].file_list = motion_list
        ic(mp_config)
        if ask_list("reproduce the motion ", ["yes", "no"]) == "yes":
            run_ts_imp_mp_controller(robot, config_file,
                                     duration=10, flag_delete_controller=False, mp_config=mp_config)

    move_forward(mp_cfg)
    move_backward(mp_cfg)


if __name__ == "__main__":
    np.set_printoptions(suppress=True, precision=3)
    main()
