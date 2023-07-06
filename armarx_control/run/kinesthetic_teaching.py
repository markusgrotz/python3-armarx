import click
from pathlib import Path
from armarx_control import console
from armarx_control.utils.file import copy_file_to_robot
from armarx_control.run.mp_forward_backward import get_control_robot, check_imp_mp_cfg, move


def teach_motion(robot, name: str):
    console.log(f"[bold cyan]Kinesthetic teaching with name {name}")
    nodeset = "RightArm"
    side = "right"
    console.log(f"[bold yellow]you can press the FT sensor of {nodeset} to start")
    traj_file_stem = robot.teach(nodeset, side, name)
    for motion_dir in ["backward", "forward"]:
        motion_file_ts = Path(f"{traj_file_stem}-ts-{motion_dir}.csv")
        motion_file_js = Path(f"{traj_file_stem}-js-{motion_dir}.csv")
        if not motion_file_ts.is_file():
            raise FileNotFoundError(f"{motion_file_ts} does not exist")
        if not motion_file_js.is_file():
            raise FileNotFoundError(f"{motion_file_js} does not exist")
        copy_file_to_robot(motion_file_ts)
        copy_file_to_robot(motion_file_js)
    traj_file_stem = Path(traj_file_stem).stem
    console.log(f"[bold cyan]using recording file {traj_file_stem} to reproduce")
    return traj_file_stem


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("--name",         "-n",   type=str,  default="", help="the absolute path to demonstration root")
@click.option("--imp_cfg_file", "-fimp", type=str, default="", help="abs path to impedance controller configuration file")
@click.option("--mp_cfg_file",  "-fmp",  type=str, default="", help="abs path to mp configuration file")
@click.option("--time_sec",     "-t",    type=float, default=5.0, help="time duration in seconds")
def main(name: str = "", imp_cfg_file: str = "", mp_cfg_file: str = "", time_sec: float = 5.0):
    if not name:
        name = "kinesthetic_teaching"

    robot = get_control_robot()
    traj_file_stem = teach_motion(robot, name)
    imp_cfg_file, mp_cfg_file, mp_cfg = check_imp_mp_cfg(imp_cfg_file, mp_cfg_file)

    move(imp_cfg_file, traj_file_stem, robot, mp_cfg, time_sec, forward=False)
    move(imp_cfg_file, traj_file_stem, robot, mp_cfg, time_sec, forward=True)
    move(imp_cfg_file, traj_file_stem, robot, mp_cfg, time_sec, forward=False)


if __name__ == "__main__":
    main()


# Note: python armarx_control/run/kinesthetic_teaching.py -t 5.0
