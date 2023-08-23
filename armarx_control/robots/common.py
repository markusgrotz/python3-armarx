import copy

import cv2
import time
import numpy as np
from pathlib import Path
from typing import Union, Dict, Tuple, List, Any
from dataclasses import dataclass
import armarx_control.utils.math as math
import armarx_control.config.common as cfg
from armarx_robots.sensors import Camera
from armarx_control import console
from armarx_control.utils.dataclass import load_dataclass
from armarx_control.utils.load_slice import load_proxy, load_slice
from armarx_vision.camera_utils import build_calibration_matrix
from armarx_control.config.common import CommonControlConfig
from armarx_control.config.njoint_controllers.taskspace_impedance import TaskspaceImpedanceControllerConfig
from armarx_control.config.njoint_controllers.taskspace_admittance import TaskspaceAdmittanceControllerConfig

load_slice("armarx_control", "../armarx/control/interface/ConfigurableNJointControllerInterface.ice")
load_slice("RobotAPI", "interface/units/RobotUnit/RobotUnitInterface.ice")

from armarx.RobotUnitModule import RobotUnitControllerManagementInterfacePrx
from armarx import NJointControllerInterfacePrx
# from armarx.control import ConfigurableNJointControllerInterfacePrx


def cast_controller(controller_ptr, controller_type: cfg.ControllerType):
    if not isinstance(controller_type, cfg.ControllerType):
        raise TypeError(f"expected controller type ControllerType, got {type(controller_type)}")

    if controller_type == cfg.ControllerType.TSImpedance:
        load_slice("armarx_control", "../armarx/control/njoint_controller/task_space/ControllerInterface.ice")
        from armarx.control import NJointTaskspaceImpedanceControllerInterfacePrx
        return NJointTaskspaceImpedanceControllerInterfacePrx.checkedCast(controller_ptr)

    elif controller_type == cfg.ControllerType.TSImpedanceMP:
        load_slice("armarx_control", "../armarx/control/njoint_mp_controller/task_space/ControllerInterface.ice")
        from armarx.control import NJointTSImpedanceMPControllerInterfacePrx
        console.log(f"cast controller for type {controller_type.value}")
        return NJointTSImpedanceMPControllerInterfacePrx.checkedCast(controller_ptr)

    # elif controller_type == cfg.ControllerType.TSBiImpedance:
    #     load_slice("armarx_control", "../armarx/control/njoint_controller/task_space/ControllerInterface.ice")
    #     from armarx.control import NJointTaskspaceBimanualImpedanceControllerInterfacePrx
    #     console.log(f"cast controller for type {controller_type.value}")
    #     return NJointTaskspaceBimanualImpedanceControllerInterfacePrx.checkedCast(controller_ptr)

    elif controller_type == cfg.ControllerType.TSAdmittance:
        load_slice("armarx_control", "../armarx/control/njoint_controller/task_space/ControllerInterface.ice")
        from armarx.control import NJointTaskspaceAdmittanceControllerInterfacePrx
        return NJointTaskspaceAdmittanceControllerInterfacePrx.checkedCast(controller_ptr)
    
    elif controller_type == cfg.ControllerType.HandController:
        load_slice("devices_ethercat", "../devices/ethercat/hand/armar6_v2/njoint_controller/ShapeInterface.ice")
        from devices.ethercat.hand.armar6_v2 import ShapeControllerInterfacePrx
        return ShapeControllerInterfacePrx.checkedCast(controller_ptr)
    else:
        console.log(f"[bold red]controller type {controller_type.value} is not supported yet")


def get_controller_config(controller_type: cfg.ControllerType, controller: NJointControllerInterfacePrx):
    if controller_type == cfg.ControllerType.TSImpedance:
        return TaskspaceImpedanceControllerConfig().from_aron_ice(controller.getConfig())
    elif controller_type == cfg.ControllerType.TSAdmittance:
        return TaskspaceAdmittanceControllerConfig().from_aron_ice(controller.getConfig())
    elif controller_type == cfg.ControllerType.TSBiImpedance:
        return TaskspaceImpedanceControllerConfig().from_aron_ice(controller.getConfig())
    elif controller_type == cfg.ControllerType.TSImpedanceMP:
        return TaskspaceImpedanceControllerConfig().from_aron_ice(controller.getConfig())
    else:
        return None


@dataclass
class ControllerData:
    ctrl: NJointControllerInterfacePrx = None
    type: cfg.ControllerType = None
    config: Any = None


class Robot:
    def __init__(self, config: Union[str, Path, Dict, cfg.RobotConfig]):
        self.c = config if isinstance(config, cfg.RobotConfig) else load_dataclass(cfg.RobotConfig, config)

        self.controllers: Dict[str, ControllerData] = {}
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
        
    def _load_hand_controller(self):
        if self.c.hand is None:
            console.log(f"[red]hand unit is not configured, skip")
            return

        hand_l = self.get_controller_by_name(self.c.hand.proxy_name_l, cfg.ControllerType.HandController)
        hand_r = self.get_controller_by_name(self.c.hand.proxy_name_r, cfg.ControllerType.HandController)
        if not hand_l.isControllerActive():
            hand_l.activateController()
        if not hand_r.isControllerActive():
            hand_r.activateController()
        self.controllers[cfg.Side.left.value] = ControllerData(
            ctrl=hand_l,
            type=cfg.ControllerType.HandController,
            config=None
        )
        self.controllers[cfg.Side.right.value] = ControllerData(
            ctrl=hand_r,
            type=cfg.ControllerType.HandController,
            config=None
        )
        ic(self.controllers.keys())

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
            controller_type: cfg.ControllerType,
            config: Union[str, CommonControlConfig],
            allow_reuse: bool = False,
            activate: bool = True
    ) -> Union[Tuple[str, NJointControllerInterfacePrx, CommonControlConfig], Tuple[None, None, None]]:
        """
        create an RT controller with the requested type.
        Args:
            control_name_prefix: the prefix of the controller name, you can set it freely to distinguish the context
            controller_type: see cfg.ControllerType for supported controller types
            config: either an absolute path to a configuration file or the Python configuration data structure
            allow_reuse: set to true will allow you to reuse the controller,
                without having to delete and recreate the controller
            activate: set to true to have an activated controller when this request is finished, otherwise, you'll
                need to activate it manually after this request

        Returns:
            controller_name: the controller name following
                'controller_creator_{control_name_prefix}_{robot_node_sets}_{controller_class_name}'
            ctrl: the proxy to the RT controller
            ctrl_cfg: the controller configuration data structure in Python

        """
        if not isinstance(controller_type, cfg.ControllerType):
            raise TypeError(f"expected controller_type ControllerType, got {type(controller_type)}")

        if isinstance(config, str):
            console.log(f"[bold cyan]create controller using {config if config else 'default config'}")
            controller_name = self.ctrl.createController(
                control_name_prefix, controller_type.value, config, activate, allow_reuse
            )
        elif isinstance(config, CommonControlConfig):
            console.log(f"[bold cyan]create controller using Aron config")
            controller_name = self.ctrl.createControllerFromAron(
                control_name_prefix, controller_type.value, config.to_aron_ice(), activate, allow_reuse
            )
        else:
            raise TypeError(f"expected config type Union[str, CommonControlConfig], got {type(config)}")

        ctrl = self.get_controller_by_name(controller_name, controller_type)
        if ctrl is None:
            console.log(f"[bold red]got null pointer to the {controller_name}, "
                        f"you need to check your interface implementation")
            return None, None, None

        if activate and not ctrl.isControllerActive():
            ctrl.activateController()
            while not ctrl.isControllerActive():
                time.sleep(0.003)

        ctrl_cfg = get_controller_config(controller_type, ctrl)
        self.controllers[controller_name] = ControllerData(
            ctrl=ctrl,
            type=controller_type,
            config=ctrl_cfg
        )
        return controller_name, ctrl, ctrl_cfg

    def teach(self, robot_node_set: cfg.NodeSet, side: str, filename: str):
        """
        Enable kinethestic teaching for the given robot node set, and filename as prefix
        Args:
            robot_node_set: RobotNodeSet name
            side: either left or right
            filename: the prefix to indicate the context of the demonstration

        Returns: the file_path = 'path_to_armarx_control_data/kinesthetic_teaching/
            {filename}-{year}-{month}-{day}-{hour}-{minute}-{second}'
            e.g. 'kinesthetic_teaching-2023-06-18-16-21-15', you will have four files recorded, including
            file_path-ts-forward.csv, file_path-ts-backward.csv, file_path-js-forward.csv, file_path-js-backward.csv
        """
        return self.ctrl.kinestheticTeaching(robot_node_set.value, side, filename)

    def update_controller_config(
            self,
            controller_name: str,
            ctrl_config: cfg.CommonControlConfig = None
    ) -> None:
        """
        update RT controller configuration by name and (optional) configuration data structure

        Args:
            controller_name: the controller name
            ctrl_config: the concrete configuration of the corresponding controller derived from CommonControlConfig
        """
        ctrl_data: ControllerData = self.controllers.get(controller_name, None)
        if ctrl_data is None:
            return
        ctrl_config = ctrl_data.config if ctrl_config is None else ctrl_config
        ctrl_data.ctrl.updateConfig(
            ctrl_config.to_aron_ice()
        )

    def get_controller_config(
            self,
            controller_name: str
    ) -> Union[CommonControlConfig, None]:
        """
        get the up-to-date controller configurations from the RT controller
        Args:
            controller_name: the controller name

        Returns: None if controller is invalid, otherwise the corresponding RT controller configuration data structure

        """
        ctrl_data: ControllerData = self.controllers.get(controller_name, None)
        if ctrl_data is None:
            return None
        return get_controller_config(
            controller_type=ctrl_data.type,
            controller=ctrl_data.ctrl
        )

    def get_controller_by_name(
            self,
            controller_name: str,
            controller_type: cfg.ControllerType
    ) -> Union[NJointControllerInterfacePrx, None]:
        """
        get the proxy of the RT controller by name
        Args:
            controller_name:
            controller_type:

        Returns: the controller proxy

        """
        if not self.robot_unit:
            console.log("[red]robot unit is not initialized")
            return None

        controllers = self.robot_unit.getAllNJointControllers()
        if controller_name not in controllers:
            console.log(f"[red]requested controller {controller_name} is not found in robot unit")
            return None

        controller = controllers[controller_name]  # type: NJointControllerInterfacePrx
        if not isinstance(controller, NJointControllerInterfacePrx):
            raise RuntimeError(f"expected controller type NJointControllerInterfacePrx, got {type(controller)}")
        return cast_controller(controller, controller_type)

    # def set_control_target(
    #         self,
    #         controller_name: str,
    #         target: Union[np.ndarray, List[float]]
    # ) -> bool:
    #     """
    #     Args:
    #         controller_name: the name of the controller
    #         target: (4, 4) matrix
    #     """
    #     # if not (np.ndim(target) == 2 and np.size(target) == 16):
    #     #     console.log(f"[red bold] invalid target pose, should be 4x4 matrix")
    #     #     return False
    #     #
    #     # ic(self.controller_cfg[controller_name].desired_pose)
    #     # if np.linalg.norm(target[:3, 3] - self.controller_cfg[controller_name].desired_pose[:3, 3]) > 50:
    #     #     console.log(f"[red bold]target pose {target} too far")
    #     #     return False
    #     # self.controller_cfg[controller_name].desired_pose = copy.deepcopy(target.astype(np.float32))
    #     # ic(self.controller_cfg[controller_name].desired_pose)
    #     # self.update_controller_config(controller_name)
    #     # return True
    #
    #     if np.ndim(target) == 2 and np.size(target) == 16:
    #         quat = math.quaternion_from_matrix(target)
    #         target = np.concatenate((target[:3, 3], quat))
    #     if np.size(target) != 7:
    #         console.log(f"[bold red]target {target} is invalid")
    #         return False
    #     if not self.ctrl.updateTargetPose(controller_name, "TSImpedance", target.flatten().tolist()):
    #         console.log(f"[bold red]update target pose failed")
    #     return True

    def deactivate(self, controller_name: str) -> bool:
        """
        deactivate the controller by name
        """
        ctrl_data = self.controllers.get(controller_name, None)
        if ctrl_data is None:
            console.log(f"controller: {controller_name} not found")
            return False
        ctrl_data.ctrl.deactivateController()
        return True

    def delete_controller(self, controller_name: str) -> bool:
        """
        deactivate and delete the controller by name
        """
        ctrl_data = self.controllers.get(controller_name, None)
        if ctrl_data is None:
            console.log(f"controller: {controller_name} not found")
            return False
        ctrl_data.ctrl.deactivateAndDeleteController()
        return True

    def close_hand(self, side: cfg.Side, finger: float, thumb: float) -> None:
        """
        close hand by setting target for finger and thumb individually
        Args:
            side: cfg.Side.left or .right or .bimanual
            finger: value from 0 (open) to 1 (closed)
            thumb: value from 0 (open) to 1 (closed)
        """
        if self.c.hand is None:
            console.log(f"[red]hand unit is not initialized")
            return
        hand = self.controllers.get(side.value, None)
        if hand is None:
            raise KeyError(f"hand {side.value} is not initialized")

        finger = max(min(1.0, finger), 0.0)
        thumb = max(min(1.0, thumb), 0.0)

        hand.ctrl.setTargetsWithPwm(
            fingers=finger, thumb=thumb,
            fingersRelativeMaxPwm=self.c.hand.max_pwm_finger, thumbRelativeMaxPwm=self.c.hand.max_pwm_thumb
        )

    def get_pose(self, node_name: str) -> np.ndarray:
        """
        return the 4 by 4 matrix representing a pose in root frame of the robot
        """
        return np.array(self.ctrl.getPoseInRootFrame(node_name), dtype=np.float32).reshape(4, 4)

    # def update_pose(self, controller_name, config, desired_pose):
    #     ctrl = self.controllers.get(controller_name, None).ctrl
    #     if ctrl is None:
    #         console.log(f"[bold red]{controller_name} is not available, check your code")
    #         return
    #     config.set_desired_pose(desired_pose)
    #     ctrl.updateConfig(config.to_aron_ice())

    def get_joint_angles(self, joint_name_lists: list = None, as_array: bool = False) -> Union[Dict[str, float], np.ndarray]:
        if joint_name_lists is None or len(joint_name_lists) == 0:
            return self.kinematic_unit.getJointAngles()
        else:
            joint_value_map = self.kinematic_unit.getJointAngles()
            return np.array([
                joint_value_map[joint_name] for joint_name in joint_name_lists
            ])

    # def get_prev_target(self, controller_name: str):
    #     # return copy.deepcopy(self.controller_cfg[controller_name].desired_pose)
    #     return np.array(self.ctrl.getPrevTargetPose(controller_name), dtype=np.float32).reshape(4, 4)

    # def get_prev_null_target(self, controller_name: str):
    #     # return copy.deepcopy(self.controller_cfg[controller_name].desired_nullspace_joint_angles)
    #     return np.array(self.ctrl.getPrevNullspaceTargetAngle(controller_name), dtype=np.float32).reshape(-1, 1)

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










