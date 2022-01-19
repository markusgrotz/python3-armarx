from armarx import slice_loader


loaded = False


def load_slice():
    global loaded
    if not loaded:
        # Implies Element.ice
        slice_loader.load_armarx_slice("RobotAPI", "ArViz/Component.ice")
        loaded = True


load_slice()
