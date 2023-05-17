import enum
import logging

import numpy as np
import typing as ty

import armarx
from armarx_memory.aron.aron_ice_types import AronIceTypes

from datetime import datetime

def pythonic_to_aron_ice(
    value: ty.Any,
) -> "armarx.aron.data.dto.GenericData":
    """
    Deeply converts objects/values of pythonic types to their Aron Ice counterparts.

    :param value: A pythonic object or value.
    :param options: Conversion options.
    :return: An Aron data Ice object.
    """
    from .ndarray.common import ndarray_to_aron

    if value is None:
        return None
    if isinstance(value, datetime):
        return AronIceTypes.datetime(value)
    if isinstance(value, str):
        return AronIceTypes.string(value)
    elif isinstance(value, bool):
        return AronIceTypes.bool(value)
    elif isinstance(value, int) or isinstance(value, np.int32):
        return AronIceTypes.int(int(value))
    elif isinstance(value, np.int64):
        return AronIceTypes.long(int(value))
    elif isinstance(value, float):
        return AronIceTypes.float(value)
    elif isinstance(value, list):
        return AronIceTypes.list(list(map(pythonic_to_aron_ice, value)))
    elif isinstance(value, enum.IntEnum):
        return pythonic_to_aron_ice(value.value)  # int

    elif isinstance(value, dict):
        a = AronIceTypes.dict({k: pythonic_to_aron_ice(v) for k, v in value.items()})
        return a

    elif isinstance(value, AronIceTypes.Dict):
        return value

    elif isinstance(value, np.ndarray):
        return ndarray_to_aron(value)

    try:
        return value.to_aron()
    except TypeError:
        pass

    raise TypeError(f"Could not convert object of type '{type(value)}' to aron.")


def pythonic_from_aron_ice(
    data: "armarx.aron.data.dto.GenericData",
    logger: ty.Optional[logging.Logger] = None,
) -> ty.Any:
    """
    Deeply converts an Aron data Ice object to its pythonic representation.

    :param data: The Aron data Ice object.
    :param logger: Logger for additional logging.
    :return: The pythonic representation.
    """
    from .ndarray.common import ndarray_from_aron

    def handle_dict(elements):
        return {k: pythonic_from_aron_ice(v) for k, v in elements.items()}

    def handle_list(elements):
        return list(map(pythonic_from_aron_ice, elements))

    if data is None:
        return None
    if isinstance(data, list):
        return handle_list(data)
    elif isinstance(data, dict):
        return handle_dict(data)

    elif isinstance(data, (float, int, str)):
        return data

    if isinstance(data, AronIceTypes.NDArray):
        return ndarray_from_aron(data)

    if isinstance(data, AronIceTypes.Long):
        return np.int64(data.value)

    try:
        return data.value
    except AttributeError:
        pass

    try:
        elements = data.elements
    except AttributeError:
        pass
    else:
        if isinstance(elements, list):
            return handle_list(elements)
        elif isinstance(elements, dict):
            return handle_dict(elements)
        else:
            raise TypeError(
                f"Could not handle aron container object of type '{type(data)}'. \n"
                f"elements: {elements}"
            )

    raise TypeError(
        f"Could not handle aron object of type '{type(data)}'.\n" f"dir(a): {dir(data)}"
    )
