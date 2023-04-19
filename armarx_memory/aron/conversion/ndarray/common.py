import numpy as np
import typing as ty

import armarx
from armarx_memory.aron.aron_ice_types import AronIceTypes
from armarx_memory.aron.conversion.ndarray.point_cloud import PointCloudConversions


dtype_rgb = [("r", "i1"), ("g", "i1"), ("b", "i1")]

# In aron objects, the data type is denoted as a string.
# dtypes_dict_to_python serves as a lookup table for aron's data type string to the python type.
dtypes_dict_to_python = {
    "float": np.float32,
    "float32": np.float32,
    "double": np.float64,
    "float64": np.float64,
    "16": dtype_rgb,  # "16" == OpenCV 8UC3 = RGB image
    # "16": np.float32,  # "16" == OpenCV F1C1 = Depth image
}
# dtypes_dict_to_aron serves as a lookup table for the python type to aron's data type string.
# As the mapping is not bijective, querying dtypes_dict_to_python in a reverse direction is not suitable.
# The python types are converted to string, as it may happen that they are unhashable (like dtype_rgb, being a list)
dtypes_dict_to_aron = {
    str(np.dtype(np.float32)): "float",
    str(np.dtype(np.float64)): "double",  # alternative: "float64"
    str(np.dtype(dtype_rgb)): "16",
}


def convert_dtype_rgb_to_int8(array: np.ndarray) -> np.ndarray:
    """
    Converts an array with shape (m, n) and dtype dtype_rgb
    to an array with shape (m, n, 3) and dtype int8.

    :param array: The RGB image with structured dtype.
    :return: The RGB image with native dtype.
    """
    return np.stack([array[c] for c in "rgb"], axis=-1)



def ndarray_to_aron(value: np.ndarray) -> AronIceTypes.NDArray:
    shape = (*value.shape, value.itemsize)
    return AronIceTypes.NDArray(
        shape=shape,
        type=dtypes_dict_to_aron[str(value.dtype)],
        data=value.tobytes(),
    )



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
        return PointCloudConversions.point_cloud_to_array(
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
