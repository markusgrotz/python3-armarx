import typing as ty

import logging


def dataclass_to_aron_ice(
        obj,
        logger: ty.Optional[logging.Logger] = None,
) -> "armarx.aron.data.dto.GenericData":
    from .dataclass_from_to_pythonic import dataclass_to_dict
    from .pythonic_from_to_ice import pythonic_to_aron

    data = dataclass_to_dict(obj, logger=logger)
    aron = pythonic_to_aron(data)
    return aron


def dataclass_from_aron_ice(
        cls,
        aron: "armarx.aron.data.dto.GenericData",
        logger: ty.Optional[logging.Logger] = None,
):
    from .dataclass_from_to_pythonic import dataclass_from_dict
    from .pythonic_from_to_ice import pythonic_from_aron

    data = pythonic_from_aron(aron)
    obj = dataclass_from_dict(cls, data, logger=logger)
    return obj
