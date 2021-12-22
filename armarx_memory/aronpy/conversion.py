import enum
import numpy as np

from typing import List, Dict

dtype_rgb = [("r", "i1"), ("g", "i1"), ("b", "i1")]

dtypes_dict = {
    "float": np.float32,
    "double": np.float64,
    "16": dtype_rgb,  # "16" == OpenCV 8UC3 = RGB image
    # "16": np.float32,  # "16" == OpenCV F1C1 = Depth image
}



def import_aron_ice():
    try:
        import armarx.aron
    except ImportError:
        from armarx import slice_loader
        slice_loader.load_armarx_slice("RobotAPI", "aron.ice")
        import armarx.aron

    return armarx.aron


try:
    class Aron:
        ARON_VERSION = "beta 0.2.3"

        ns = import_aron_ice().data.dto

        Data = ns.GenericData

        String = ns.AronString
        Bool = ns.AronBool
        Int = ns.AronInt
        Long = ns.AronLong
        Float = ns.AronFloat

        List = ns.List
        Dict = ns.Dict

        NDArray = ns.NDArray

        @classmethod
        def string(cls, value: str):
            return cls.String(value=value, VERSION=cls.ARON_VERSION)

        @classmethod
        def bool(cls, value: int):
            return cls.Bool(value=value, VERSION=cls.ARON_VERSION)

        @classmethod
        def int(cls, value: int):
            return cls.Int(value=value, VERSION=cls.ARON_VERSION)

        @classmethod
        def long(cls, value: int):
            return cls.Long(value=value, VERSION=cls.ARON_VERSION)

        @classmethod
        def float(cls, value: float):
            return cls.Float(value=value, VERSION=cls.ARON_VERSION)

        @classmethod
        def list(cls, elements: list):
            return cls.List(elements=elements, VERSION=cls.ARON_VERSION)

        @classmethod
        def dict(cls, elements: dict):
            return cls.Dict(elements=elements, VERSION=cls.ARON_VERSION)



except AttributeError as e:

    class Aron:

        ns = import_aron_ice().data

        Data = ns.AronData

        String = ns.AronString
        Bool = ns.AronBool
        Int = ns.AronInt
        Long = ns.AronLong
        Float = ns.AronFloat

        List = ns.AronList
        Dict = ns.AronDict

        NdArray = ns.AronNDArray


def to_aron(value) -> "armarx.aron.data.dto.GenericData":

    if isinstance(value, str):
        return Aron.string(value)
    elif isinstance(value, bool):
        return Aron.bool(value)
    elif isinstance(value, int) or isinstance(value, np.int32):
        return Aron.int(int(value))
    elif isinstance(value, np.int64):
        return Aron.long(int(value))
    elif isinstance(value, float):
        return Aron.float(value)
    elif isinstance(value, list):
        return Aron.list(list(map(to_aron, value)))
    elif isinstance(value, enum.IntEnum):
        return to_aron(value.value)  # int

    elif isinstance(value, dict):
        a = Aron.dict({k: to_aron(v) for k, v in value.items()})
        return a

    elif isinstance(value, Aron.Dict):
        return value

    elif isinstance(value, np.ndarray):
        shape = (*value.shape, value.itemsize)
        return Aron.NDArray(shape=shape, type=str(value.dtype), data=value.tobytes())

    try:
        return value.to_aron()
    except TypeError:
        pass

    raise TypeError(f"Could not convert object of type '{type(value)}' to aron.")


def from_aron(a: "armarx.aron.data.dto.GenericData"):
    def handle_dict(elements):
        return {k: from_aron(v) for k, v in elements.items()}

    def handle_list(elements):
        return list(map(from_aron, elements))

    if a is None:
        return None
    if isinstance(a, list):
        return handle_list(a)
    elif isinstance(a, dict):
        return handle_dict(a)
    elif isinstance(a, (float, int, str)):
        return a

    if isinstance(a, Aron.NdArray):
        # Last entry is #bytes per entry
        data: bytes = a.data
        dtype = dtypes_dict[a.type]

        shape: List[int]
        try:
            shape = a.dimensions[:-1]
        except AttributeError:
            shape = a.shape[:-1]

        array: np.ndarray = np.frombuffer(buffer=data, dtype=dtype)
        array = array.reshape(shape)
        return array

    try:
        return a.value
    except AttributeError:
        pass

    try:
        elements = a.elements
    except AttributeError:
        pass
    else:
        if isinstance(elements, list):
            return handle_list(elements)
        elif isinstance(elements, dict):
            return handle_dict(elements)
        else:
            raise TypeError(f"Could not handle aron container object of type '{type(a)}'. \n"
                            f"elements: {elements}")

    raise TypeError(f"Could not handle aron object of type '{type(a)}'.\n"
                    f"dir(a): {dir(a)}")


def convert_dtype_rgb_to_int8(array: np.ndarray) -> np.ndarray:
    """
    Converts an array with shape (m, n) and dtype dtype_rgb
    to an array with shape (m, n, 3) and dtype int8.
    :param array: The RGB image with structured dtype.
    :return: The RGB image with native dtype.
    """
    return np.stack([array[c] for c in "rgb"], axis=-1)
