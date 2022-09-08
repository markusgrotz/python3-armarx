import enum

import numpy as np
import typing as ty

from .aron_ice_types import AronIceTypes, dtypes_dict


def pythonic_to_aron(value) -> "armarx.aron.data.dto.GenericData":
    """
    Deeply converts objects/values of pythonic types to their Aron Ice counterparts.

    :param value: A pythonic object or value.
    :return: An Aron data Ice object.
    """

    if value is None:
        return None
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
        return AronIceTypes.list(list(map(pythonic_to_aron, value)))
    elif isinstance(value, enum.IntEnum):
        return pythonic_to_aron(value.value)  # int

    elif isinstance(value, dict):
        a = AronIceTypes.dict({k: pythonic_to_aron(v) for k, v in value.items()})
        return a

    elif isinstance(value, AronIceTypes.Dict):
        return value

    elif isinstance(value, np.ndarray):
        shape = (*value.shape, value.itemsize)
        return AronIceTypes.NDArray(shape=shape, type=str(value.dtype), data=value.tobytes())

    try:
        return value.to_aron()
    except TypeError:
        pass

    raise TypeError(f"Could not convert object of type '{type(value)}' to aron.")


def pythonic_from_aron(data: "armarx.aron.data.dto.GenericData"):
    """
    Deeply converts an Aron data Ice object to its pythonic representation.

    :param data: The Aron data Ice object.
    :return: The pythonic representation.
    """
    def handle_dict(elements):
        return {k: pythonic_from_aron(v) for k, v in elements.items()}

    def handle_list(elements):
        return list(map(pythonic_from_aron, elements))

    if data is None:
        return None
    if isinstance(data, list):
        return handle_list(data)
    elif isinstance(data, dict):
        return handle_dict(data)
    elif isinstance(data, (float, int, str)):
        return data

    if isinstance(data, AronIceTypes.NDArray):
        # Last entry is #bytes per entry
        data: bytes = data.data

        shape: ty.Tuple[int]
        try:
            shape = data.dimensions[:-1]
        except AttributeError:
            shape = data.shape[:-1]
        shape = tuple(shape)

        dtype = dtypes_dict.get(data.type, None)
        if dtype is None:
            size = np.product(shape)
            if size == 0:
                dtype = np.uint8
            else:
                dtype_size = len(data) // size
                dtype_dict = {
                    1: np.uint8,
                    2: np.uint16,
                    4: np.uint32,
                    8: np.uint64
                }
                dtype = dtype_dict.get(dtype_size, None)
                if dtype is None:
                    # Build a structured dtype with sequence of bytes.
                    dtype = np.dtype([("bytes", np.uint8, dtype_size)])

            print(f"Unknown type '{data.type}' of array with shape {shape} and {len(data)} bytes. "
                  f"Falling back to {dtype}.")

        array: np.ndarray = np.frombuffer(buffer=data, dtype=dtype)
        array = array.reshape(shape)
        return array

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
            raise TypeError(f"Could not handle aron container object of type '{type(data)}'. \n"
                            f"elements: {elements}")

    raise TypeError(f"Could not handle aron object of type '{type(data)}'.\n"
                    f"dir(a): {dir(data)}")
