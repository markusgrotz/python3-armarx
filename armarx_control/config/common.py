import json
from marshmallow_dataclass import dataclass
from armarx_control.utils.dataclass import default_field
from armarx_memory.aron.aron_dataclass import AronDataclass
from enum import Enum


class NodeSet(Enum):
    pass


class TCP(Enum):
    pass


class Side(Enum):
    left = "left_hand"
    right = "right_hand"
    bimanual = "left_hand,right_hand"


class ControllerType(Enum):
    TSAdmittance = "TSAdmittance"
    TSImpedance = "TSImpedance"
    TSBiImpedance = "TSBiImpedance"
    KptAdmittance = "KptAdmittance"
    KptImpedance = "KptImpedance"
    TSAdmittanceMP = "TSAdmittanceMP"
    TSImpedanceMP = "TSImpedanceMP"
    TSBiImpedanceMP = "TSBiImpedanceMP"
    KptAdmittanceMP = "KptAdmittanceMP"
    KptImpedanceMP = "KptImpedanceMP"
    KVILImpedanceMP = "KVILImpedanceMP"
    QPWholeBodyImpedance = "QPWholeBodyImpedance"
    QPWholeBodyVelocity = "QPWholeBodyVelocity"
    HandController = "HandController"


class Coordination(Enum):
    unimanual = 0
    uncoordinated = 1
    loosely_coupled = 2

    # TODO add more


@dataclass
class CommonControlConfig(AronDataclass):
    @classmethod
    def _get_conversion_options(cls):
        from armarx_memory.aron.conversion import ConversionOptions
        return ConversionOptions(
            names_snake_case_to_camel_case=True,
            names_python_to_aron_dict={},
        )

    def from_json(self, config_filename: str):
        with open(config_filename) as file:
            json_config = json.load(file)

        def convert_dict_array_data(dict_cfg: dict, result_dict: dict):
            for k, v in dict_cfg.items():
                if isinstance(v, dict):
                    if v.get("data", None) is not None and v.get("dims") is not None:
                        result_dict[k] = v.get("data")
                    else:
                        if result_dict.get(k, None) is None:
                            result_dict[k] = {}
                        convert_dict_array_data(v, result_dict[k])
                else:
                    result_dict[k] = v

        converted_config = {}
        convert_dict_array_data(json_config, converted_config)
        return self.from_dict(converted_config)


@dataclass
class StereoCameraConfig:
    proxy_name:         str = "RCImageProvider"
    frame_name_l:       str = "roboception_left"
    frame_name_r:       str = "roboception_right"
    base_line_dist:     float = 160.00001194725948

    intrinsic_l:        list = default_field([
        [1074.8825683594, 0, 640.0000000000],
        [0, 1074.8825683594, 480.0000000000],
        [0, 0, 1]
    ])
    intrinsic_r:        list = default_field([
        [1074.8825683594, 0, 640.0000000000],
        [0, 1074.8825683594, 480.0000000000],
        [0, 0, 1]
    ])
    image_dimension:    tuple = None
    image_format:       dict = None
    number_of_images:   int = 0


@dataclass
class MonocularCameraConfig:
    proxy_name:         str = "OpenNIPointCloudProvider"
    frame_name:         str = "AzureKinectCamera"
    image_dimension:    tuple = None
    image_format:       dict = None
    number_of_images:   int = 0
    intrinsic:          list = default_field([[1., 0, 1], [0, 1., ], [0, 0, 1.]])


@dataclass
class HandUnitConfig:
    proxy_name_l:       str = "Hand_L_EEF_NJointKITHandV2ShapeController"
    proxy_name_r:       str = "Hand_R_EEF_NJointKITHandV2ShapeController"
    max_pwm_finger:     float = 1.0
    max_pwm_thumb:      float = 1.0
    type:               str = "HandController"


@dataclass
class ControllerCreatorConfig:
    proxy_name:         str = "controller_creator"


@dataclass
class KinematicUnitConfig:
    proxy_name:         str = "Armar6KinematicUnit"


@dataclass
class RobotUnitConfig:
    proxy_name:         str = "Armar6Unit"


@dataclass
class RobotStateConfig:
    proxy_name:         str = "RobotStateComponent"


@dataclass
class PlatformUnitConfig:
    proxy_name:         str = "Armar6PlatformUnit"


@dataclass
class RobotConfig:
    stereo:             StereoCameraConfig = None
    mono:               MonocularCameraConfig = None
    ctrl:               ControllerCreatorConfig = None
    kinematic:          KinematicUnitConfig = None
    hand:               HandUnitConfig = None
    robot_unit:         RobotUnitConfig = None
    platform:           PlatformUnitConfig = None
    state:              RobotStateConfig = None
