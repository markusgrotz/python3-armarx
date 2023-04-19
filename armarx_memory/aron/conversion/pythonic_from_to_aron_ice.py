import enum
import logging

import numpy as np
import typing as ty

import armarx
from armarx_memory.aron.aron_ice_types import AronIceTypes, dtypes_dict_to_python, dtypes_dict_to_aron
from armarx_memory.aron.conversion.options import ConversionOptions


def pythonic_to_aron_ice(
    value: ty.Any,
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


def ndarray_to_aron(value: np.ndarray) -> AronIceTypes.NDArray:
    shape = (*value.shape, value.itemsize)
    return AronIceTypes.NDArray(
        shape=shape,
        type=dtypes_dict_to_aron[str(value.dtype)],
        data=value.tobytes(),
    )


class PointClouds:
    dtype_point_color_xyz = np.dtype([
        ("position", np.float32, (4,)), ("color", np.uint32), ("padding", np.uint8, (12,))
    ])
    dtype_point_xyz_color_label = np.dtype([
        ("position", np.float32, (4,)), ("color", np.uint32), ("label", np.int32)
    ])

    point_type_string_dtype_to_dict = {
        # "XYZ": dtype_point_xyz,
        "XYZRGBA": dtype_point_color_xyz,
        # "XYZL": dtype_point_xyz_label,
        "XYZRGBL": dtype_point_xyz_color_label,
        # "XYZI": dtype_point_xyz_intensity,
        # "XYZNormal": dtype_point_normal_xyz,
        # "XYZRGBANormal": dtype_point_color_normal_xyz,
    }

    dtype_to_point_type_string_dict = {
        v: k for k, v in point_type_string_dtype_to_dict.items()
    }

    @classmethod
    def dtype_from_point_type_string(cls, point_type: str):
        original_argument = point_type

        if point_type.startswith("pcl::"):
            point_type = point_type[len("pcl::"):]

        assert point_type.startswith("Point"), point_type
        point_type = point_type[len("Point"):]

        dtype = cls.point_type_string_dtype_to_dict.get(point_type, None)
        if dtype is not None:
            return dtype
        else:
            raise Exception(f"Point type '{original_argument}' not supported yet.")

    @classmethod
    def dtype_without_paddings(cls, pcl_dtype: np.dtype) -> np.dtype:
        fields = []
        for key, (dtype, offset) in pcl_dtype.fields.items():
            if key == "padding":
                continue

            if dtype.subdtype is None:
                subdtype = dtype
                shape = None
            else:
                subdtype, shape = dtype.subdtype

            if key == "position":
                assert shape == (4,)
                shape = (3,)

            if shape is None:
                fields.append((key, subdtype))
            else:
                fields.append((key, subdtype, shape))

        return np.dtype(fields)

    @classmethod
    def point_cloud_without_paddings(cls, point_cloud: np.ndarray) -> np.ndarray:
        # Remove paddings to dtypes defined for point cloud providers/processors.
        new_dtype = cls.dtype_without_paddings(point_cloud.dtype)
        new_point_cloud = np.zeros(point_cloud.shape, dtype=new_dtype)
        for key in new_point_cloud.dtype.fields:
            sub_array = point_cloud[key]
            if key == "position":
                sub_array = sub_array[..., :3]

            new_point_cloud[key] = sub_array

        return new_point_cloud

    @classmethod
    def point_cloud_to_array(
            cls,
            byte_data: bytes,
            type_str: str,
            shape: ty.Tuple,
            bytes_per_element: int,
    ):
        pcl_dtype = PointClouds.dtype_from_point_type_string(type_str)
        assert pcl_dtype.itemsize == bytes_per_element, f"{pcl_dtype.itemsize} == {bytes_per_element}"

        array: np.ndarray = np.frombuffer(buffer=byte_data, dtype=pcl_dtype)
        array = array.reshape(shape)
        assert array.shape == shape, f"{array.shape} == {shape}"

        point_cloud = PointClouds.point_cloud_without_paddings(array)
        return point_cloud


def ndarray_from_aron(data: AronIceTypes.NDArray) -> np.ndarray:
    byte_data: bytes = data.data

    # Last entry is #bytes per element.
    shape: ty.Tuple[int]
    try:
        bytes_per_element = data.dimensions[-1]
        shape = data.dimensions[:-1]
    except AttributeError:
        bytes_per_element = data.shape[-1]
        shape = data.shape[:-1]
    shape = tuple(shape)

    if "pcl::" in data.type:
        return PointClouds.point_cloud_to_array(
            byte_data=byte_data, type_str=data.type, shape=shape, bytes_per_element=bytes_per_element)

    dtype = dtypes_dict_to_python.get(data.type, None)

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
