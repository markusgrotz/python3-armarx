import time
import click
import numpy as np
from pathlib import Path

from armarx_control import console
from armarx_control.robots.common import cfg, Robot
from armarx_control.utils.pkg import get_armarx_package_data_dir
from armarx_control.utils.interact import ask_list
from armarx_control.config.mp.mp_config import MPListConfig


def get_control_robot():
    c = cfg.RobotConfig()
    c.robot_unit = cfg.RobotUnitConfig()
    c.kinematic_unit = cfg.KinematicUnitConfig()
    c.ctrl = cfg.ControllerCreatorConfig()
    c.hand = cfg.HandUnitConfig()
    c.platform = cfg.PlatformUnitConfig()
    return Robot(c)


def run_ts_imp_mp_controller(
        robot: Robot,
        config_filename: str,
        duration: float = 5.0,
        flag_delete_controller: bool = True,
        mp_config: MPListConfig = None
):
    control_type = "TSImpedanceMP"
    rns_right = "RightArm"
    tcp_right = "Hand R TCP"
    target_pose = []

    controller_name, ctrl, cfg = robot.create_controller(
        "python_reproduction", rns_right, control_type, config_filename, True
    )

    try:
        current_pose = robot.get_controller_config(controller_name).get_desired_pose_vector()
        ctrl.updateMPConfig(mp_config.to_aron_ice())
        ctrl.learnFromCSV([])
        console.log(f"[bold cyan]Start with current pose: \n{current_pose}, target pose: \n{target_pose}")
        input("continue? ... ")
        ctrl.start("default", current_pose, target_pose, duration)

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
        console.log(f"target pose right: \n{robot.get_controller_config(controller_name).get_desired_pose()}")

    except RuntimeError as e:
        console.log(f"error: {e}")
    finally:
        if flag_delete_controller:
            console.log(f"[bold green]deleting controller")
            robot.delete_controller(controller_name)
        console.rule("done")


def move(
        imp_cfg_file: str,
        traj_file_stem: str,
        robot: Robot,
        mp_config: MPListConfig,
        time_sec: float,
        forward: bool = True
):
    dir_str = "forward" if forward else "backward"
    console.rule(f"[bold cyan]running {dir_str} MP ...")
    motion_list = [str("/home/armar-user/armar6_motion/kinesthetic_teaching/" + f"{traj_file_stem}-ts-{dir_str}.csv")]
    console.log(f"[yellow]using motion list {motion_list}")
    mp_config.mp_list[0].file_list = motion_list
    if ask_list("return in a reversed way? ", ["yes", "no"]) == "yes":
        run_ts_imp_mp_controller(robot, str(imp_cfg_file),
                                 duration=time_sec, mp_config=mp_config)


def check_imp_mp_cfg(imp_cfg_file: str = "", mp_cfg_file: str = ""):
    controller_type = "NJointTSImpedanceMPController"
    pkg_path = get_armarx_package_data_dir("armarx_control")
    if not imp_cfg_file or not Path(imp_cfg_file).is_file():
        imp_cfg_file = pkg_path / f"controller_config/{controller_type}/default.json"
        if not imp_cfg_file.is_file():
            raise FileNotFoundError(f"{imp_cfg_file} does not exist")
    if not mp_cfg_file or not Path(mp_cfg_file).is_file():
        mp_cfg_file = pkg_path / f"controller_config/{controller_type}/default_mp.json"
        if not mp_cfg_file.is_file():
            raise FileNotFoundError(f"{mp_cfg_file} does not exist")
    return imp_cfg_file, mp_cfg_file, MPListConfig().from_json(str(mp_cfg_file))


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("--filename",     "-f",    type=str,      help="abs path to the recorded traj (end before -forward/-backward")
@click.option("--imp_cfg_file", "-fimp", type=str, default="", help="abs path to impedance controller configuration file")
@click.option("--mp_cfg_file",  "-fmp",  type=str, default="", help="abs path to mp configuration file")
@click.option("--time_sec",     "-t",    type=float, default=5.0, help="time duration in seconds")
def reproduction(filename: str, imp_cfg_file: str = "", mp_cfg_file: str = "", time_sec: float = 5.0):
    imp_cfg_file, mp_cfg_file, mp_cfg = check_imp_mp_cfg(imp_cfg_file, mp_cfg_file)
    robot = get_control_robot()
    move(imp_cfg_file, filename, robot, mp_cfg, time_sec, forward=True)
    move(imp_cfg_file, filename, robot, mp_cfg, time_sec, forward=False)


if __name__ == "__main__":
    np.set_printoptions(suppress=True, precision=3)
    reproduction()


# Note: python armarx_control/run/mp_forward_backward.py -f kinesthetic_teaching-2023-06-18-16-21-15-ts -t 5.0
