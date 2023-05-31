


class ArmarXCoreError(Exception):
    """
    Base class of Exceptions raised by the ArmarX Python Bindings.
    """
    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
