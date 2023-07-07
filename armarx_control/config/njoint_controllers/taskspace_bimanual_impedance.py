from taskspace_impedance import TaskspaceImpedanceControllerConfig
from armarx_control.config.common import CommonControlConfig, dataclass, default_field


@dataclass
class TSBiImpedanceConfig(CommonControlConfig):
    config_left:  TaskspaceImpedanceControllerConfig = default_field(TaskspaceImpedanceControllerConfig())
    config_right: TaskspaceImpedanceControllerConfig = default_field(TaskspaceImpedanceControllerConfig())

    def __post_init__(self):
        self.config_left.__post_init__()
        self.config_right.__post_init__()


if __name__ == "__main__":
    from armarx_control.utils.pkg import get_armarx_package_data_dir

    p = get_armarx_package_data_dir("armarx_control")
    p = p / "controller_config/NJointTaskspaceBimanualImpedanceController/default.json"
    if not p.is_file():
        raise FileExistsError(f"{p} does not exist")
    c = TSBiImpedanceConfig().from_json(str(p))
    ic(c.to_aron_ice())
