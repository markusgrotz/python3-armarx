import time
import numpy as np
from armarx_control import console
from armarx_control.robots.common import cfg, Robot, pose_to_vec


def main():
    np.set_printoptions(suppress=True, precision=3)

    c = cfg.RobotConfig()
    c.robot_unit = cfg.RobotUnitConfig("Armar6Unit")
    c.kinematic_unit = cfg.KinematicUnitConfig("Armar6KinematicUnit")
    c.ctrl = cfg.ControllerCreatorConfig()
    c.hand = cfg.HandUnitConfig()
    c.platform = cfg.PlatformUnitConfig()
    robot = Robot(c)

    filename = robot.teach("RightArm", "right", "approach_kettle")
    console.log(f"[bold cyan]writing to {filename}")


if __name__ == "__main__":
    main()
