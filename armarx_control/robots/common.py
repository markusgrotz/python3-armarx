import copy

import cv2
import time
import numpy as np
from pathlib import Path
from typing import Union, Dict, Tuple, List, Any

import armarx_control.utils.math as math
import armarx_control.config.common as cfg
from armarx_robots.sensors import Camera
from armarx_control import console
from armarx_control.utils.dataclass import load_dataclass
from armarx_control.utils.load_slice import load_proxy, load_slice
from armarx_vision.camera_utils import build_calibration_matrix
from armarx_control.utils.pkg import get_armarx_package_data_dir
from armarx_control.config.njoint_controllers.taskspace_impedance import TaskspaceImpedanceControllerConfig

load_slice("armarx_control", "../armarx/control/interface/ConfigurableNJointControllerInterface.ice")
load_slice("RobotAPI", "interface/units/RobotUnit/RobotUnitInterface.ice")

from armarx.RobotUnitModule import RobotUnitControllerManagementInterfacePrx
from armarx import NJointControllerInterfacePrx
# from armarx.control import ConfigurableNJointControllerInterfacePrx


def cast_controller(controller_ptr, controller_type: str):
    if controller_type == "TSImpedance":
        load_slice("armarx_control", "../armarx/control/njoint_controller/task_space/ControllerInterface.ice")
        from armarx.control import NJointTaskspaceImpedanceControllerInterfacePrx
        return NJointTaskspaceImpedanceControllerInterfacePrx.checkedCast(controller_ptr)

    elif controller_type == "TSImpedanceMP":
        load_slice("armarx_control", "../armarx/control/njoint_mp_controller/task_space/ControllerInterface.ice")
        from armarx.control import NJointTSImpedanceMPControllerInterfacePrx
        console.log(f"cast controller for type {controller_type}")
        return NJointTSImpedanceMPControllerInterfacePrx.checkedCast(controller_ptr)

    elif controller_type == "TSAdmittance":
        load_slice("armarx_control", "../armarx/control/njoint_controller/task_space/ControllerInterface.ice")
        from armarx.control import NJointTaskspaceAdmittanceControllerInterfacePrx
        return NJointTaskspaceAdmittanceControllerInterfacePrx.checkedCast(controller_ptr)
    
    elif controller_type == "HandController":
        load_slice("devices_ethercat", "../devices/ethercat/hand/armar6_v2/njoint_controller/ShapeInterface.ice")
        from devices.ethercat.hand.armar6_v2 import ShapeControllerInterfacePrx
        return ShapeControllerInterfacePrx.checkedCast(controller_ptr)
    else:
        console.log(f"[bold red]controller type {controller_type} is not supported yet")


class Robot:
    def __init__(self, config: Union[str, Path, Dict, cfg.RobotConfig]):
        self.c = config if isinstance(config, cfg.RobotConfig) else load_dataclass(cfg.RobotConfig, config)

        self.controllers = {}       # type: Dict[str, Any]
        self.controller_cfg = {}    # type: Dict[str, Any]
        self._load_mono_cam()
        self._load_stereo_cam()
        self._load_kinematic_unit()
        self._load_robot_unit()
        self._load_ctrl_creator()

        self._load_hand_controller()
        self._load_platform_unit()

    def _load_kinematic_unit(self):
        if self.c.kinematic is None:
            console.log(f"[red]Kinematic unit is not configured, skip")
            return

        from armarx import KinematicUnitInterfacePrx
        self.kinematic_unit = KinematicUnitInterfacePrx.get_proxy(self.c.kinematic.proxy_name)

    def _load_mono_cam(self):
        if self.c.mono is None:
            console.log(f"[red]Azure kinect is not configured, skip")
            return

        self.mono = Camera(self.c.mono.proxy_name)
        self.mono_proxy = self.mono.proxy
        if not self.mono_proxy:
            console.log(f"[red]monocular camera is not available, please check {self.c.mono.proxy_name}")
            return

        self.c.mono.frame_name = self.mono.reference_frame_name
        self.c.mono.image_format = image_format = self.mono.image_format
        self.c.mono.number_of_images = self.mono.num_images
        console.log('[bold cyan]monocular image format: {}'.format(image_format))
        self.c.mono.image_dimension = (
            # (2, 720, 1280, 3)
            self.c.mono.number_of_images,
            image_format.dimension.height,
            image_format.dimension.width,
            image_format.bytesPerPixel
        )
        self.c.mono.intrinsic = build_calibration_matrix(self.mono.calibration["left"])
        # self.c.mono.intrinsic = np.array([
        #     [710.9051513671875, 0, 635.4113159179688],
        #     [0, 710.9051513671875, 354.36126708984375],
        #     [0, 0, 1]
        # ])
        console.log(f'[bold green]data dimensions {self.c.mono.image_dimension} with intrinsic {self.c.mono.intrinsic}')

    def _load_stereo_cam(self):
        if self.c.stereo is None:
            console.log(f"[red]stereo camera is not configured, skip")
            return

        self.stereo = Camera(self.c.stereo.proxy_name)
        self.stereo_proxy = self.stereo.proxy
        if not self.stereo_proxy:
            console.log(f"[red]stereo camera is not available, please check {self.c.stereo.proxy_name}")
            return

        self.c.stereo.frame_name_l = self.stereo.reference_frame_name
        self.c.stereo.frame_name_r = self.c.stereo.frame_name_l.replace("Left", "Right")
        self.c.stereo.image_format = image_format = self.stereo.image_format
        self.c.stereo.number_of_images = self.stereo.num_images
        console.log('[bold cyan]stereo image format {}'.format(image_format))
        self.c.stereo.image_dimension = (
            # (2, 720, 1280, 3)
            self.c.stereo.number_of_images,
            image_format.dimension.height,
            image_format.dimension.width,
            image_format.bytesPerPixel
        )
        calib = self.stereo.calibration
        self.c.stereo.intrinsic_l = build_calibration_matrix(calib["left"])
        self.c.stereo.intrinsic_r = build_calibration_matrix(calib["right"])
        console.log('[bold green]data dimensions {}'.format(self.c.stereo.image_dimension))

    def _load_robot_unit(self):
        if self.c.robot_unit is None:
            console.log(f"[red]robot unit is not configured, skip")
            self.robot_unit = None
            return

        self.robot_unit = load_proxy(self.c.robot_unit.proxy_name, RobotUnitControllerManagementInterfacePrx)

    def _load_platform_unit(self):
        if self.c.robot_unit is None:
            console.log(f"[red]platform unit is not configured, skip")
            self.platform_unit = None
            return

        load_slice("RobotAPI", "interface/units/PlatformUnitInterface.ice")
        from armarx import PlatformUnitInterfacePrx
        self.platform_unit = load_proxy(self.c.platform.proxy_name, PlatformUnitInterfacePrx)

    def _load_ctrl_creator(self):
        if self.c.ctrl is None:
            console.log(f"[red]controller builder is not configured, skip")
            self.ctrl = None
            return

        load_slice("armarx_control", "../armarx/control/components/controller_creator/ComponentInterface.ice")
        from armarx.control.components.controller_creator import ComponentInterfacePrx
        self.ctrl = load_proxy(self.c.ctrl.proxy_name, ComponentInterfacePrx)

        # load_slice("RobotControllers", "components/kvil/KVILInterface.ice")
        # from armarx.RobotControllers.components.kvil import KVILInterfacePrx
        # self.ctrl = load_proxy(self.c.ctrl.proxy_name, KVILInterfacePrx)
        
    def _load_hand_controller(self):
        if self.c.hand is None:
            console.log(f"[red]hand unit is not configured, skip")
            return

        self.controllers[f"left_hand"] = self.get_controller_by_name(self.c.hand.proxy_name_l, self.c.hand.type)
        if not self.controllers["left_hand"].isControllerActive():
            self.controllers["left_hand"].activateController()
        self.controllers[f"right_hand"] = self.get_controller_by_name(self.c.hand.proxy_name_r, self.c.hand.type)
        if not self.controllers["left_hand"].isControllerActive():
            self.controllers["left_hand"].activateController()

    def _load_robot_state_component(self):
        if self.c.state is None:
            console.log(f"[red]hand unit is not configured, skip")
            return

        from armarx import RobotStateComponentInterfacePrx
        self.state = RobotStateComponentInterfacePrx.get_proxy()

    def get_stereo_frames(self) -> Union[None, Tuple[np.ndarray, np.ndarray, float]]:
        if not self.ctrl:
            console.log(f"[red]controller builder is not initialized")
            return None
        left_cam_pose = np.array(self.ctrl.getPoseInRootFrame(self.c.stereo.frame_name_l)).reshape(4, 4)
        right_cam_pose = np.array(self.ctrl.getPoseInRootFrame(self.c.stereo.frame_name_r)).reshape(4, 4)
        console.log(f"[bold green]left frame: {left_cam_pose}, right frame: {right_cam_pose}")
        base_line_dist = np.linalg.norm(left_cam_pose[:3, -1] - right_cam_pose[:3, -1])
        return left_cam_pose, right_cam_pose, base_line_dist

    def get_stereo_images(self) -> Tuple[np.ndarray, Dict]:
        image_buffer, info = self.stereo_proxy.getImagesAndMetaInfo()
        return np.frombuffer(image_buffer, dtype=np.uint8).reshape(self.c.stereo.image_dimension), info

    def get_mono_images(
            self,
            depth_unit_in_meter: bool,
            resize_wh: tuple = None
    ) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Get azure kinect images, return [rgb, depth] images as a tuple
        """
        image_buffer, info = self.mono_proxy.getImagesAndMetaInfo()
        images = np.frombuffer(image_buffer, dtype=np.uint8).reshape(self.c.mono.image_dimension)
        rgb = images[0]
        r = images[1][:, :, 0]
        g = images[1][:, :, 1]
        depth = np.left_shift(g.astype(np.uint64), 8).astype(np.float64) + r.astype(np.uint64)
        if depth_unit_in_meter:
            depth *= 0.001

        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
        if resize_wh is not None:
            rgb = cv2.resize(rgb, resize_wh)
            depth = cv2.resize(depth, resize_wh)
        return rgb, depth, info

    def create_controller(
            self,
            control_name_prefix: str,
            robot_node_set: str,
            controller_type: str,
            config_filename: str
    ):
        controller_name = self.ctrl.createController(control_name_prefix, robot_node_set, controller_type, config_filename)
        ctrl = self.get_controller_by_name(controller_name, controller_type)
        if ctrl is None:
            console.log(f"[bold red]got null pointer to the {controller_name}, "
                        f"you need to check your interface implementation")
            exit(1)
        self.controllers[controller_name] = ctrl

        init_taskspace_target = self.get_prev_target(controller_name)
        init_nullspace_target = self.get_prev_null_target(controller_name)

        # TODO, this is here because we don't have the interface to retrieve the current controller configs yet
        if controller_type == "TSImpedance":
            json_file = get_armarx_package_data_dir(
                "armarx_control") / f"controller_config/NJointTaskspaceImpedanceController/default.json"
            config = TaskspaceImpedanceControllerConfig().from_json(str(json_file))
            config.desired_pose = init_taskspace_target
            config.desired_nullspace_joint_angles = init_nullspace_target
            self.controller_cfg[controller_name] = config
        else:
            config = None
            console.log(f"[bold red]controller config in Python for type {controller_type} is not supported yet.")
        # TODO when it is possible to retieve config directly,
        # config = TaskspaceImpedanceControllerConfig().from_aron_ice(ctrl.getUpToDateConfig())

        return controller_name, ctrl, config

    def teach(self, kinematic_chain: str, side: str, filename: str):
        return self.ctrl.kinestheticTeaching(kinematic_chain, side, filename)

    def update_controller_config(self, controller_name: str):
        self.controllers[controller_name].updateConfig(self.controller_cfg[controller_name].to_aron_ice())

    def get_controller_by_name(self, controller_name: str, controller_type: str):
        if not self.robot_unit:
            console.log("[red]robot unit is not initialized")
            return None

        controllers = self.robot_unit.getAllNJointControllers()
        if controller_name not in controllers:
            console.log(f"[red]requested controller {controller_name} is not found in robot unit")
            return None

        controller = controllers[controller_name]  # type: NJointControllerInterfacePrx
        assert isinstance(controller, NJointControllerInterfacePrx)
        return cast_controller(controller, controller_type)

    def set_control_target(
            self,
            controller_name: str,
            target: Union[np.ndarray, List[float]]
    ) -> bool:
        """
        Args:
            controller_name: the name of the controller
            target: (4, 4) matrix
        """
        # if not (np.ndim(target) == 2 and np.size(target) == 16):
        #     console.log(f"[red bold] invalid target pose, should be 4x4 matrix")
        #     return False
        #
        # ic(self.controller_cfg[controller_name].desired_pose)
        # if np.linalg.norm(target[:3, 3] - self.controller_cfg[controller_name].desired_pose[:3, 3]) > 50:
        #     console.log(f"[red bold]target pose {target} too far")
        #     return False
        # self.controller_cfg[controller_name].desired_pose = copy.deepcopy(target.astype(np.float32))
        # ic(self.controller_cfg[controller_name].desired_pose)
        # self.update_controller_config(controller_name)
        # return True

        if np.ndim(target) == 2 and np.size(target) == 16:
            quat = math.quaternion_from_matrix(target)
            target = np.concatenate((target[:3, 3], quat))
        if np.size(target) != 7:
            console.log(f"[bold red]target {target} is invalid")
            return False
        if not self.ctrl.updateTargetPose(controller_name, "TSImpedance", target.flatten().tolist()):
            console.log(f"[bold red]update target pose failed")
        return True

    def deactivate(self, controller_name: str):
        ctrl = self.controllers.get(controller_name, None)
        if ctrl is None:
            console.log(f"controller: {controller_name} not found")
            return False
        ctrl.deactivateController()
        return True

    def delete_controller(self, controller_name: str):
        ctrl = self.controllers.get(controller_name, None)
        if ctrl is None:
            console.log(f"controller: {controller_name} not found")
            return False
        ctrl.deactivateAndDeleteController()
        return True

    def close_hand(self, side: cfg.Side, finger: float, thumb: float):
        if self.c.hand is None:
            console.log(f"[red]hand unit is not initialized")
            return
        finger = max(min(1.0, finger), 0.0)
        thumb = max(min(1.0, thumb), 0.0)
        # self.kvil_cmp.closeHand(side, finger, thumb)
        name = "left_hand" if side == cfg.Side.left else "right_hand"
        self.controllers[name].setTargetsWithPwm(
            fingers=finger, thumb=thumb,
            fingersRelativeMaxPwm=self.c.hand.max_pwm_finger, thumbRelativeMaxPwm=self.c.hand.max_pwm_thumb
        )

    def get_pose(self, node_name: str) -> np.ndarray:
        """
        return the 4 by 4 matrix representing a pose in root frame of the robot
        """
        return np.array(self.ctrl.getPoseInRootFrame(node_name), dtype=np.float32).reshape(4, 4)

    def get_joint_angles(self, joint_name_lists: list = None) -> Dict[str, float]:
        if joint_name_lists is None or len(joint_name_lists) == 0:
            return self.kinematic_unit.getJointAngles()
        else:
            raise NotImplementedError

    def get_prev_target(self, controller_name: str):
        # return copy.deepcopy(self.controller_cfg[controller_name].desired_pose)
        return np.array(self.ctrl.getPrevTargetPose(controller_name), dtype=np.float32).reshape(4, 4)

    def get_prev_null_target(self, controller_name: str):
        # return copy.deepcopy(self.controller_cfg[controller_name].desired_nullspace_joint_angles)
        return np.array(self.ctrl.getPrevNullspaceTargetAngle(controller_name), dtype=np.float32).reshape(-1, 1)

    def set_platform_vel(self, velocity: Union[list, np.ndarray]):
        """
        unit [x: mm/s, y: mm/s, r: radian/s]
        """
        if np.size(velocity) != 3:
            console.log(f"[bold red]velocity not valid, must be a 3-D list or np.ndarray")
            return
        if isinstance(velocity, np.ndarray):
            velocity = velocity.tolist()
        # return self.ctrl.setPlatformVelocity(velocity)
        self.platform_unit.move(velocity[0], velocity[1], velocity[2])

    # def look_at(self, position: np.ndarray, use_stereo: bool = False):
    #     if np.size(position) != 3:
    #         console.log(f"[bold red]invalid position, must be 3-D np.ndarray")
    #         return
    #
    #     if use_stereo:
    #         pose_l, pose_r, _ = self.get_stereo_frames()
    #         cam_center_pose = pose_l
    #         cam_center_pose[:3, 3] = (pose_r[:3, 3] + pose_l[:3, 3]) * 0.5


def framed_pose_to_vec(framed_pose: dict):
    return np.array([
        framed_pose["x"],
        framed_pose["y"],
        framed_pose["z"],
        framed_pose["qw"],
        framed_pose["qx"],
        framed_pose["qy"],
        framed_pose["qz"],
    ])


def pose_to_vec(pose_matrix: np.ndarray):
    if np.shape(pose_matrix) != (4, 4):
        raise ValueError(f"pose matrix {pose_matrix} is supposed to be a (4, 4) np.ndarray")
    pose = np.zeros(7, dtype=float)
    pose[3:] = math.quaternion_from_matrix(pose_matrix)
    pose[:3] = pose_matrix[:3, 3]
    return pose


def vec_to_pose(pose_vec: np.ndarray):
    if not (np.ndim(pose_vec) == 1 and np.size(pose_vec) == 7):
        raise ValueError(f"Vector {pose_vec} must have 7 dimensions.")
    pose = math.quaternion_matrix(pose_vec[3:])
    pose[:3, 3] = pose_vec[:3]
    return pose


if __name__ == "__main__":
    np.set_printoptions(suppress=True, precision=3)

    c = cfg.RobotConfig()
    # c.mono = cfg.MonocularCameraConfig()
    # c.stereo = cfg.StereoCameraConfig()
    c.robot_unit = cfg.RobotUnitConfig("Armar6Unit")
    c.kinematic_unit = cfg.KinematicUnitConfig("Armar6KinematicUnit")
    c.ctrl = cfg.ControllerCreatorConfig()
    c.hand = cfg.HandUnitConfig()
    c.platform = cfg.PlatformUnitConfig()
    robot = Robot(c)

    for i in range(100):
        robot.set_platform_vel([0, -100, 0])
        time.sleep(0.01)
    for i in range(100):
        robot.set_platform_vel([0, 100, 0])
        time.sleep(0.01)
    robot.set_platform_vel([0, 0, 0])

    control_type = "TSImpedance"  # "TSAdmittance"
    rns_left = "LeftArm"
    rns_right = "RightArm"
    tcp_left = "Hand L TCP"
    tcp_right = "Hand R TCP"
    controller_name_l, ctrl_l, cfg_l = robot.create_controller("python", rns_left, control_type, "")
    controller_name_r, ctrl_r, cfg_r = robot.create_controller("python", rns_right, control_type, "")

    try:
        init_target_pose_l = robot.get_prev_target(controller_name_l)
        init_target_pose_r = robot.get_prev_target(controller_name_r)
        init_null_target_l = robot.get_prev_null_target(controller_name_l)
        init_null_target_r = robot.get_prev_null_target(controller_name_r)

        json_file = get_armarx_package_data_dir("armarx_control") / "controller_config/NJointTaskspaceImpedanceController/default.json"
        config_l = TaskspaceImpedanceControllerConfig().from_json(str(json_file))
        config_l.desired_pose = init_target_pose_l
        config_l.desired_nullspace_joint_angles = init_null_target_l
        ic(config_l)
        # config_aron_ice = config.to_aron_ice()
        # ic(config_aron_ice)
        # ic(type(config_aron_ice))

        # console.rule("set target")
        ctrl_l.updateConfig(config_l.to_aron_ice())
        # assert False
        # console.rule("done")

        console.log("close hands")
        robot.close_hand(cfg.Side.left, 1.0, 1.0)
        robot.close_hand(cfg.Side.right, 1.0, 1.0)
        time.sleep(1)
        console.log("open hands")
        robot.close_hand(cfg.Side.left, 0, 0)
        robot.close_hand(cfg.Side.right, 0, 0)
        time.sleep(1)

        # target_left = copy.deepcopy(init_target_pose_l)
        # target_right = copy.deepcopy(init_target_pose_r)
        target_left = copy.deepcopy(robot.get_pose(tcp_left))
        target_right = copy.deepcopy(robot.get_pose(tcp_right))
        console.log(f"Initial target, left: \n{target_left} \nand right: \n{target_right}")
        console.log(f"current_pose, left: \n{robot.get_pose(tcp_left)} \nand right: \n{robot.get_pose(tcp_right)}")

        n_steps = 500
        pose_z_range_left = np.linspace(target_left[2, 3], target_left[2, 3] + 300.0, n_steps)
        pose_z_range_right = np.linspace(target_right[2, 3], target_right[2, 3] + 300.0, n_steps)
        finger_range_left = np.linspace(0, 1, n_steps)
        finger_range_right = np.linspace(0, 1, n_steps)
        t = 0
        dt = 0.01
        for i in range(n_steps):
            target_left[2, 3] = pose_z_range_left[i]
            target_right[2, 3] = pose_z_range_right[i]
            robot.close_hand(cfg.Side.left, finger_range_left[i], finger_range_left[i])
            robot.close_hand(cfg.Side.right, finger_range_right[i], finger_range_right[i])
            config_l.desired_pose = target_right
            # ctrl_l.updateConfig(config_l.to_aron_ice())
            robot.set_control_target(controller_name_l, target_left)
            robot.set_control_target(controller_name_r, target_right)
            time.sleep(dt)
            t += dt

        ic(config_l)

        console.log(f"current_pose, left: \n{robot.get_pose(tcp_left)} \n"
                    f"and right: \n{robot.get_pose(tcp_right)}")
        console.log(f"target pose : left: \n{robot.get_prev_target(controller_name_l)} \n"
                    f"and right: \n{robot.get_prev_target(controller_name_r)}")

    except RuntimeError as e:
        console.log(f"error: {e}")
    finally:
        robot.close_hand(cfg.Side.left, 0, 0)
        robot.close_hand(cfg.Side.right, 0, 0)
        robot.delete_controller(controller_name_l)
        robot.delete_controller(controller_name_r)









