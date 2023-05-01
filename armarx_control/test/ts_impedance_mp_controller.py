import time
import numpy as np
from armarx_control import console
from armarx_control.robots.common import cfg, Robot, pose_to_vec


def main():
    np.set_printoptions(suppress=True, precision=3)

    c = cfg.RobotConfig()
    c.robot_unit = cfg.RobotUnitConfig()
    c.kinematic_unit = cfg.KinematicUnitConfig()
    c.ctrl = cfg.ControllerCreatorConfig()
    c.hand = cfg.HandUnitConfig()
    c.platform = cfg.PlatformUnitConfig()
    robot = Robot(c)

    control_type = "TSImpedanceMP"
    rns_right = "RightArm"
    tcp_right = "Hand R TCP"
    config_filename = ""
    # config_filename = "/common/homes/staff/gao/projects/control/python3-armarx/armarx_control/test/config/approach_kettle.json"
    controller_name_r, ctrl_r, cfg_r = robot.create_controller("python", rns_right, control_type, config_filename)

    try:
        init_target_pose_r = robot.get_prev_target(controller_name_r)
        init_null_target_r = robot.get_prev_null_target(controller_name_r)

        current_pose_r = pose_to_vec(init_target_pose_r)
        target_pose_r = init_target_pose_r
        target_pose_r[2, 3] += 300
        target_pose_r = pose_to_vec(target_pose_r)

        console.log("[bold blue]Learning from demonstration")
        ctrl_r.learnFromCSV([])
        console.log("[bold blue]Starting VMP controller")
        input("confirm ... ")
        console.log(f"current pose right: \n{current_pose_r}")
        console.log(f"target pose right: \n{target_pose_r}")
        duration = 5.0
        input("start? ... ")
        ctrl_r.start("default", current_pose_r, target_pose_r, duration)
        console.log("[bold yellow]controller is running")

        console.log("close hands")
        robot.close_hand(cfg.Side.left, 1.0, 1.0)
        robot.close_hand(cfg.Side.right, 1.0, 1.0)
        time.sleep(1)

        _start = time.time()
        while True:
            time.sleep(0.001)
            console.log(f"canonical value: {ctrl_r.getCanVal('default')}")
            if (time.time() - _start) > duration:
                console.log("[bold green]VMP controller finished")
                break

        console.log("open hands")
        robot.close_hand(cfg.Side.left, 0, 0)
        robot.close_hand(cfg.Side.right, 0, 0)
        time.sleep(1)

        console.log(f"current_pose right: \n{robot.get_pose(tcp_right)}")
        console.log(f"target pose right: \n{robot.get_prev_target(controller_name_r)}")

    except RuntimeError as e:
        console.log(f"error: {e}")
    finally:
        robot.close_hand(cfg.Side.left, 0, 0)
        robot.close_hand(cfg.Side.right, 0, 0)
        robot.delete_controller(controller_name_r)


if __name__ == "__main__":
    main()
