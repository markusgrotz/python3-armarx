from armarx_control.utils.pkg import get_armarx_package_data_dir
from armarx_control.config.njoint_controllers.taskspace_impedance import TaskspaceImpedanceControllerConfig


json_file = get_armarx_package_data_dir("armarx_control") / "controller_config/NJointTaskspaceImpedanceController/default.json"
config = TaskspaceImpedanceControllerConfig().from_json(str(json_file))
ic(config)
config_aron_ice = config.to_aron_ice()
ic(config_aron_ice)
config_py = TaskspaceImpedanceControllerConfig().from_aron_ice(config_aron_ice)
ic(config_py)

