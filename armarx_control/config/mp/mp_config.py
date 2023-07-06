import copy
import numpy as np
from typing import List, Any
from dataclasses import dataclass, field
from armarx_control.config.common import CommonControlConfig


def default_field(obj: Any):
    return field(default_factory=lambda: copy.deepcopy(obj))


@dataclass
class ListViaPoint(CommonControlConfig):
    canonical_value:    np.float64 = 0.0
    via_point_value:    List[np.float64] = default_field([])

@dataclass
class MPConfig(CommonControlConfig):
    name:               str = "default"
    class_name:         str = "TSMP"
    mp_type_string:     str = "TaskSpacePrincipalComponent"
    mp_mode:            str = "Linear"
    mp_style:           str = "Discrete"
    regression_model:   str = "default"
    kernel_size:        int = 20
    damping:            np.float32 = 20.0
    tau:                np.float64 = 1.0
    amplitude:          np.float64 = 1.0
    duration_sec:       np.float64 = 5.0

    file_list:          List[str] = default_field([])
    stop_with_mp:       bool = True
    via_points:         List[ListViaPoint] = default_field([])

    enable_phase_stop:  bool = False
    max_value:          np.float64 = 10.0
    slop:               np.float64 = 10.0
    go_dist:            np.float64 = 50.0
    back_dist:          np.float64 = 10.0
    ps_kp_pos:          np.float64 = 1.0
    ps_kd_pos:          np.float64 = 2.
    ps_kp_ori:          np.float64 = 1.
    ps_kd_ori:          np.float64 = 0.1
    ps_mm_2_radian:     np.float64 = 10.

    @classmethod
    def _get_conversion_options(cls):
        from armarx_memory.aron.conversion import ConversionOptions
        return ConversionOptions(
            names_snake_case_to_camel_case=True,
            names_python_to_aron_dict=dict(
                stop_with_mp="stopWithMP",
                ps_mm_2_radian="psMM2Radian",
            ),
        )


@dataclass
class MPListConfig(CommonControlConfig):
    mp_list:            List[MPConfig] = default_field([])


if __name__ == "__main__":
    from armarx_control.utils.pkg import get_armarx_package_data_dir
    p = get_armarx_package_data_dir("armarx_control")
    p = p / "controller_config/NJointTSImpedanceMPController/default_mp.json"
    if not p.is_file():
        raise FileExistsError(f"{p} does not exist")
    c = MPListConfig().from_json(str(p))
    ic(c.to_aron_ice())
    ic(isinstance(c.mp_list[0].damping, np.float32))
    ic(isinstance(c.mp_list[0].tau, np.float64))
    ic(isinstance(c.mp_list[0].tau, float))

    # cc = MPConfig()
    # cc.damping = np.float32(20.0)
    # cc.tau = np.float64(1.0)
    # ic(cc.to_aron_ice())

