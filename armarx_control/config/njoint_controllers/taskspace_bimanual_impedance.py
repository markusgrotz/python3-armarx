from taskspace_impedance import TSImpedanceConfig
from armarx_control.config.common import CommonControlConfig


@dataclass
class TSBiImpedanceConfig(CommonControlConfig):
    config_left:  TSImpedanceConfig
    config_right: TSImpedanceConfig

    def __post_init__(self):
        self.config_left.__post_init__()
        self.config_right.__post_init__()

