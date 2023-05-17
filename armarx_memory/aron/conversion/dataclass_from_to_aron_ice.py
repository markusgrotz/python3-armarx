import typing as ty

import logging

def to_aron_ice(
        data,
        logger: ty.Optional[logging.Logger] = None,
) -> "armarx.aron.data.dto.GenericData":
    from .pythonic_from_to_aron_ice import pythonic_to_aron_ice
    
    if logger is not None:
        logger.debug("Convert Pythonic types to ARON Ice DTOs ...")
    aron = pythonic_to_aron_ice(data)

    return aron


def from_aron_ice(
        aron: "armarx.aron.data.dto.GenericData",
        logger: ty.Optional[logging.Logger] = None,
):
    from .pythonic_from_to_aron_ice import pythonic_from_aron_ice

    if logger is not None:
        logger.debug("Convert ARON Ice DTOs to Pythonic types ...")
    return pythonic_from_aron_ice(aron, logger=logger)


def dataclass_to_aron_ice(
    obj,
    logger: ty.Optional[logging.Logger] = None,
) -> "armarx.aron.data.dto.GenericData":
    from .dataclass_from_to_pythonic import dataclass_to_dict
    from .pythonic_from_to_aron_ice import pythonic_to_aron_ice

    if logger is not None:
        logger.debug(f"Convert object of ARON dataclass {type(obj)} to Pythonic types  ...")
    data = dataclass_to_dict(obj, logger=logger)

    return to_aron_ice(data, logger=logger)


def dataclass_from_aron_ice(
    cls,
    aron: "armarx.aron.data.dto.GenericData",
    logger: ty.Optional[logging.Logger] = None,
):
    from .dataclass_from_to_pythonic import dataclass_from_dict
    from .pythonic_from_to_aron_ice import pythonic_from_aron_ice

    data = from_aron_ice(aron, logger=logger)

    if logger is not None:
        logger.debug(f"Convert Pythonic types to ARON dataclass {cls} ...")
    obj = dataclass_from_dict(cls, data, logger=logger)

    return obj
