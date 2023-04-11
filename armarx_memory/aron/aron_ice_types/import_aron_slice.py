def import_aron_slice():
    """
    Import and return the aron slice module.
    :return: The aron slice module.
    """

    def handle_error():
        import armarx
        from armarx_core import slice_loader

        slice_loader.load_armarx_slice("RobotAPI", "aron.ice")

    try:
        from armarx import aron

        # import armarx.aron
    except ImportError:
        handle_error()
        from armarx import aron

    return aron
