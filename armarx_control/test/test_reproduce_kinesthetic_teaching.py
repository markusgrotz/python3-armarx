import time
import click
from pathlib import Path
import numpy as np
from armarx_control import console
from armarx_control.robots.common import cfg, Robot, pose_to_vec
from armarx_control.utils.pkg import get_armarx_package_data_dir
from armarx_control.utils.file import copy_file_to_robot
from robot_utils.py.utils import load_dict_from_yaml, save_to_yaml
from robot_utils.py.filesystem import validate_file
from robot_utils.py.interact import ask_list
import json

# 'paramiko',  # required for ssh connection, copy files, etc
# 'scp',
# from paramiko import SSHClient, SSHException
# from scp import SCPClient
#
#
# ssh_info = {
#     'hostname': '10.6.2.100',
#     'port': 22,
#     'username': "armar-user",
#     'timeout': 5
# }
#
#
# def copy_to_robot(filename: Path):
#     with SSHClient() as ssh:
#         ssh.load_system_host_keys()
#         try:
#             ssh.connect(**ssh_info)
#         except SSHException as ex:
#             console.print(f"[bold red]{ex}")
#             console.log(f"[bold red]Cannot connect to {ssh_info}")
#             return None
#         try:
#             with SCPClient(ssh.get_transport()) as scp:
#                 if filename.is_file():
#                     folder = "/home/armar-user/armar6_motion/kinesthetic_teaching"
#                     scp.put(str(filename), folder, recursive=True)
#                     console.rule("control config sent to robot")
#                     return Path(folder) / filename.name
#                 else:
#                     console.log(f"[bold red]{filename} doesn't exist")
#                     return None
#         except RuntimeError:
#             console.log(f"ssh copy failed")


def run_ts_imp_mp_controller(robot: Robot, config_filename: Path, duration: float = 5.0):
    control_type = "TSImpedanceMP"
    rns_right = "RightArm"
    tcp_right = "Hand R TCP"
    target_pose = []
    validate_file(config_filename, throw_error=True)

    controller_name_r, ctrl_r, cfg_r = robot.create_controller(
        "kvil_deploy", rns_right, control_type, str(config_filename), True
    )

    try:
        current_pose_r = pose_to_vec(robot.get_prev_target(controller_name_r))
        ctrl_r.learnFromCSV([])
        console.log(f"[bold cyan]Start with current pose: \n{current_pose_r}, target pose: \n{target_pose}")
        input("continue? ... ")
        ctrl_r.start("default", current_pose_r, target_pose, duration)

        _start = time.time()
        ready_to_stop = False
        while True:
            time.sleep(0.001)
            if ctrl_r.isFinished("default") and not ready_to_stop:
                _start = time.time()
                console.log("[bold green]VMP controller finished")
                ready_to_stop = True

            if ready_to_stop and (time.time() - _start) > 1.5:
                console.log("[bold green]stop impedance controller")
                break

        console.log(f"current_pose right: \n{robot.get_pose(tcp_right)}")
        console.log(f"target pose right: \n{robot.get_prev_target(controller_name_r)}")

    except RuntimeError as e:
        console.log(f"error: {e}")
    finally:
        robot.delete_controller(controller_name_r)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("--filename",     "-f",   type=str,      help="filename of the recorded traj (before -forward/-backward")
def main(filename):
    controller_type = "NJointTSImpedanceMPController"
    config_file = get_armarx_package_data_dir("armarx_control") / f"controller_config/{controller_type}/default.json"
    mp_config = load_dict_from_yaml(config_file)
    current_dir = Path(__file__).parent
    np.set_printoptions(suppress=True, precision=3)

    c = cfg.RobotConfig()
    c.robot_unit = cfg.RobotUnitConfig()
    c.kinematic_unit = cfg.KinematicUnitConfig()
    c.ctrl = cfg.ControllerCreatorConfig()
    c.hand = cfg.HandUnitConfig()
    c.platform = cfg.PlatformUnitConfig()
    robot = Robot(c)

    nodeset = "RightArm"
    side = "right"

    console.log(f"[bold green]preparing the mp config")
    mp_cfg = mp_config["mpList"][0]
    if mp_cfg["name"] != "default":
        raise ValueError("the mp name should be set to 'default'")

    def move_backward():
        # motion_file = validate_file(f"{filename}-ts-backward.csv", throw_error=True)[0]
        # motion_file = copy_file_to_robot(motion_file)
        mp_cfg["fileList"] = [str("/home/armar-user/armar6_motion/kinesthetic_teaching/" + f"{filename}-backward.csv")]
        controller_config_filename = current_dir / "config/teaching_backward.json"
        with open(controller_config_filename, 'w') as fp:
            json.dump(mp_config, fp, sort_keys=True, indent=4)
        if ask_list("return in a reversed way? ", ["yes", "no"]) == "yes":
            run_ts_imp_mp_controller(robot, controller_config_filename, duration=2)

    def move_forward():
        # motion_file = validate_file(f"{filename}-ts-forward.csv", throw_error=True)[0]
        # motion_file = copy_file_to_robot(motion_file)
        mp_cfg["fileList"] = [str("/home/armar-user/armar6_motion/kinesthetic_teaching/" + f"{filename}-forward.csv")]
        controller_config_filename = current_dir / "config/teaching_forward.json"
        with open(controller_config_filename, 'w') as fp:
            json.dump(mp_config, fp, sort_keys=True, indent=4)
        if ask_list("reproduce the motion ", ["yes", "no"]) == "yes":
            run_ts_imp_mp_controller(robot, controller_config_filename, duration=2)

    move_forward()
    move_backward()


if __name__ == "__main__":
    main()
