import numpy as np

from typing import List, Dict

dtypes_dict = {
    "float": np.float32,
    "double": np.float64,
}


def import_aron_ice():
    try:
        import armarx.aron
    except ImportError:
        from armarx import slice_loader
        slice_loader.load_armarx_slice("RobotAPI", "aron.ice")
        import armarx.aron

    return armarx.aron


def to_aron(value) -> "armarx.aron.data.AronData":
    aron_ice = import_aron_ice()

    if isinstance(value, str):
        return aron_ice.data.AronString(value)
    elif isinstance(value, int) or isinstance(value, np.int32):
        return aron_ice.data.AronInt(int(value))
    elif isinstance(value, np.int64):
        return aron_ice.data.AronLong(int(value))
    elif isinstance(value, float):
        return aron_ice.data.AronFloat(value)
    elif isinstance(value, list):
        return aron_ice.data.AronList(list(map(to_aron, value)))

    elif isinstance(value, dict):
        a = aron_ice.data.AronDict({})
        for k, v in value.items():
            a.elements[k] = to_aron(v)
        return a

    elif isinstance(value, aron_ice.data.AronDict):
        return value

    try:
        return value.to_aron()
    except TypeError:
        pass

    raise TypeError(f"Could not convert object of type '{type(value)}' to aron.")


def from_aron(a: "armarx.aron.data.AronData"):
    def handle_dict(elements):
        return {k: from_aron(v) for k, v in elements.items()}

    def handle_list(elements):
        return list(map(from_aron, elements))

    if isinstance(a, list):
        return handle_list(a)
    elif isinstance(a, dict):
        return handle_dict(a)
    elif isinstance(a, str) or isinstance(a, int) or isinstance(a, float):
        return a

    aron_ice = import_aron_ice()

    if isinstance(a, aron_ice.data.AronNDArray):
        # Last entry is #bytes per entry
        data: bytes = a.data
        dtype = dtypes_dict[a.type]
        shape: List[int] = a.dimensions[:-1]

        array: np.ndarray = np.frombuffer(buffer=data, dtype=dtype)
        array = array.reshape(shape)
        return array

    try:
        return a.value
    except AttributeError:
        pass

    try:
        elements = a.elements
        if isinstance(elements, list):
            return handle_list(elements)
        elif isinstance(elements, dict):
            return handle_dict(elements)
    except AttributeError:
        pass

    raise TypeError(f"Could not handle aron object of type '{type(a)}'.")
