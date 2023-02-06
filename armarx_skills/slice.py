import armarx_core

loaded = False


def load_slice():
    global loaded
    if not loaded:
        armarx_core.slice_loader.load_armarx_slice("RobotAPI", "skills/SkillProviderInterface.ice")
        armarx_core.slice_loader.load_armarx_slice("RobotAPI", "skills/SkillManagerInterface.ice")
        loaded = True
