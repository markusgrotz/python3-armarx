import numpy as np
from typing import Optional, Dict
from dataclasses import dataclass, field
from armarx_control.utils.math import pose_to_vec, vec_to_pose
from armarx_control.config.common import CommonControlConfig, default_field


@dataclass
class TSImpedanceConfig(CommonControlConfig):
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
        # console.log(f"[bold red]Warning: the pose is transposed during conversion from CPP to Python"
        #             f"due to column-major to row-major representation, I manually transposed the pose for you. "
        #             f"This will be fixed in the future.")
        return self.desired_pose

    def set_desired_pose(self, desired_pose: np.ndarray):
        # console.log(f"[bold red]Warning: the pose is transposed during conversion from CPP to Python"
        #             f"due to column-major to row-major representation, I manually transposed the pose for you. "
        #             f"This will be fixed in the future.")
        self.desired_pose = desired_pose.astype(np.float32)

    def get_desired_pose_vector(self):
        return pose_to_vec(self.get_desired_pose())

    def set_desired_pose_vector(self, desired_pose_vector: np.ndarray):
        self.set_desired_pose_vector(vec_to_pose(desired_pose_vector))


@dataclass
class TaskspaceImpedanceControllerConfig(CommonControlConfig):
    cfg:  Dict[str, TSImpedanceConfig] = default_field({})

    @classmethod
    def _get_conversion_options(cls):
        from armarx_memory.aron.conversion import ConversionOptions
        return ConversionOptions(
            names_snake_case_to_camel_case=True,
            names_python_to_aron_dict={"RightArm": "RightArm", "LeftArm": "LeftArm"},
        )


if __name__ == "__main__":
    from armarx_control.utils.pkg import get_armarx_package_data_dir

    p = get_armarx_package_data_dir("armarx_control")
    p = p / "controller_config/NJointTSImpedanceMPController/default.json"
    # p = p / "controller_config/NJointTaskspaceBimanualImpedanceController/default.json"
    if not p.is_file():
        raise FileExistsError(f"{p} does not exist")
    c = TaskspaceImpedanceControllerConfig().from_json(str(p))
    ic(c)
    ic(c.cfg.keys())
    ic(c.to_aron_ice())
    c.cfg
    d = TaskspaceImpedanceControllerConfig.from_aron_ice(c.to_aron_ice())
    ic(d)
