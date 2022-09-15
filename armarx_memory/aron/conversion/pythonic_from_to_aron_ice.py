import enum

import numpy as np
import typing as ty

from armarx_memory.aron.aron_ice_types import AronIceTypes, dtypes_dict
from armarx_memory.aron.conversion.options import ConversionOptions


def pythonic_to_aron_ice(
    value: ty.Any,
    options: ty.Optional[ConversionOptions] = None,
) -> "armarx.aron.data.dto.GenericData":
    """
    Deeply converts objects/values of pythonic types to their Aron Ice counterparts.

    :param value: A pythonic object or value.
    :param options: Conversion options.
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
        return AronIceTypes.list(list(map(pythonic_to_aron_ice, value)))
    elif isinstance(value, enum.IntEnum):
        return pythonic_to_aron_ice(value.value)  # int

    elif isinstance(value, dict):
        a = AronIceTypes.dict(
            {
                (
                    options.name_python_to_aron(k) if options is not None else k
                ): pythonic_to_aron_ice(v)
                for k, v in value.items()
            }
        )
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
    options: ty.Optional[ConversionOptions] = None,
) -> ty.Any:
    """
    Deeply converts an Aron data Ice object to its pythonic representation.

    :param data: The Aron data Ice object.
    :param options: Conversion options.
    :return: The pythonic representation.
    """

    def handle_dict(elements):
        return {
            (
                options.name_aron_to_python(k) if options is not None else k
            ): pythonic_from_aron_ice(v)
            for k, v in elements.items()
        }

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


def ndarray_to_aron(value: np.ndarray) -> AronIceTypes.NDArray:
    shape = (*value.shape, value.itemsize)
    return AronIceTypes.NDArray(
        shape=shape, type=str(value.dtype), data=value.tobytes()
    )


def ndarray_from_aron(data: AronIceTypes.NDArray) -> np.ndarray:
    # Last entry is #bytes per entry
    byte_data: bytes = data.data

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
            dtype_size = len(byte_data) // size
            dtype_dict = {1: np.uint8, 2: np.uint16, 4: np.uint32, 8: np.uint64}
            dtype = dtype_dict.get(dtype_size, None)
            if dtype is None:
                # Build a structured dtype with sequence of bytes.
                dtype = np.dtype([("bytes", np.uint8, dtype_size)])

        print(
            f"Unknown type '{data.type}' of array with shape {shape} and {len(byte_data)} bytes. "
            f"Falling back to {dtype}."
        )

    array: np.ndarray = np.frombuffer(buffer=byte_data, dtype=dtype)
    array = array.reshape(shape)
    return array
