import typing as ty

import logging

from .options import ConversionOptions


def dataclass_to_aron_ice(
    obj,
    options: ty.Optional[ConversionOptions] = None,
    logger: ty.Optional[logging.Logger] = None,
) -> "armarx.aron.data.dto.GenericData":
    from .dataclass_from_to_pythonic import dataclass_to_dict
    from .pythonic_from_to_aron_ice import pythonic_to_aron_ice

    data = dataclass_to_dict(obj, logger=logger)
    aron = pythonic_to_aron_ice(data, options=options)
    return aron


def dataclass_from_aron_ice(
    cls,
    aron: "armarx.aron.data.dto.GenericData",
    options: ty.Optional[ConversionOptions] = None,
    logger: ty.Optional[logging.Logger] = None,
):
    from .dataclass_from_to_pythonic import dataclass_from_dict
    from .pythonic_from_to_aron_ice import pythonic_from_aron_ice

    data = pythonic_from_aron_ice(aron, options=options)
    obj = dataclass_from_dict(cls, data, logger=logger)
    return obj
