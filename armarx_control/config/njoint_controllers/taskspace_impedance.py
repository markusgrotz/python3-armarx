import numpy as np
from typing import Optional
from dataclasses import dataclass, field
from armarx_control import console
from armarx_control.utils.math import pose_to_vec, vec_to_pose
from armarx_control.config.common import CommonControlConfig


@dataclass
class TSImpedanceConfig:
    node_set_name: str = ""
    kp_impedance: np.ndarray = field(default_factory=lambda: np.zeros((6, 1), dtype=np.float32))
    kd_impedance: np.ndarray = field(default_factory=lambda: np.zeros((6, 1), dtype=np.float32))

    kp_nullspace: np.ndarray = field(default_factory=lambda: np.zeros((1, 1), dtype=np.float32))
    kd_nullspace: np.ndarray = field(default_factory=lambda: np.zeros((1, 1), dtype=np.float32))

    desired_pose: np.ndarray = field(default_factory=lambda: np.zeros((4, 4), dtype=np.float32))
    desired_twist: np.ndarray = field(default_factory=lambda: np.zeros((6, 1), dtype=np.float32))

    desired_nullspace_joint_angles: Optional[np.ndarray] = field(default_factory=lambda: np.zeros((1, 1), dtype=np.float32))

    torque_limit: float = 0.0
    qvel_filter: float = 0.0

    def __post_init__(self):
        self.kp_impedance = np.array(self.kp_impedance, dtype=np.float32).reshape(6, 1)
        self.kd_impedance = np.array(self.kd_impedance, dtype=np.float32).reshape(6, 1)

        self.kp_nullspace = np.array(self.kp_nullspace, dtype=np.float32).reshape(-1, 1)
        self.kd_nullspace = np.array(self.kp_nullspace, dtype=np.float32).reshape(-1, 1)

        self.desired_pose = np.array(self.desired_pose, dtype=np.float32).reshape(4, 4)
        self.desired_twist = np.array(self.desired_twist, dtype=np.float32).reshape(6, 1)

        if self.desired_nullspace_joint_angles is not None:
            self.desired_nullspace_joint_angles = np.array(self.desired_nullspace_joint_angles, dtype=np.float32).reshape(-1, 1)

        self.torque_limit = float(self.torque_limit)
        self.qvel_filter = float(self.qvel_filter)

    def get_desired_pose(self):
        console.log(f"[bold red]Warning: the pose is transposed during conversion from CPP to Python"
                    f"due to column-major to row-major representation, I manually transposed the pose for you. "
                    f"This will be fixed in the future.")
        return self.desired_pose.T

    def set_desired_pose(self, desired_pose: np.ndarray):
        console.log(f"[bold red]Warning: the pose is transposed during conversion from CPP to Python"
                    f"due to column-major to row-major representation, I manually transposed the pose for you. "
                    f"This will be fixed in the future.")
        self.desired_pose = desired_pose.T.astype(np.float32)

    def get_desired_pose_vector(self):
        return pose_to_vec(self.get_desired_pose())

    def set_desired_pose_vector(self, desired_pose_vector: np.ndarray):
        self.set_desired_pose_vector(vec_to_pose(desired_pose_vector))


@dataclass
class TaskspaceImpedanceControllerConfig(CommonControlConfig, TSImpedanceConfig):
    pass
