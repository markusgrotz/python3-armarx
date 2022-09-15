"""
This module provides functionality for receiving and providing point clouds in ArmarX.

Classes:
- PointCloudProvider: Can provide point clouds as numpy arrays.
"""

from typing import Tuple, List

import numpy as np

from visionx import PointCloudProviderInterfacePrx
from visionx import PointCloudProviderInterface
from visionx import PointCloudProcessorInterfacePrx
from visionx import PointCloudProcessorInterface
from visionx import MetaPointCloudFormat
from visionx import PointContentType


# Structured data types for point types defined in VisionX
# These are binary compatible with the Blob data used by PointCloudProvider
dtype_point_xyz = np.dtype([("position", np.float32, (3,))])
dtype_point_color_xyz = np.dtype([("color", np.uint32), ("position", np.float32, (3,))])
dtype_point_normal_xyz = np.dtype(
    [("normal", np.float32, (3,)), ("position", np.float32, (3,))]
)
dtype_point_color_normal_xyz = np.dtype(
    [("color", np.uint32), ("normal", np.float32, (3,)), ("position", np.float32, (3,))]
)
dtype_point_xyz_label = np.dtype([("position", np.float32, (3,)), ("label", np.int32)])
dtype_point_xyz_color_label = np.dtype(
    [("position", np.float32, (3,)), ("color", np.uint32), ("label", np.int32)]
)
dtype_point_xyz_intensity = np.dtype(
    [("position", np.float32, (3,)), ("intensity", np.float32)]
)


# Color as RGBA
dtype_point_rgba_xyz = np.dtype(
    [
        ("r", np.uint8),
        ("g", np.uint8),
        ("b", np.uint8),
        ("a", np.uint8),
        ("position", np.float32, (3,)),
    ]
)
dtype_point_rgba_normal_xyz = np.dtype(
    [
        ("r", np.uint8),
        ("g", np.uint8),
        ("b", np.uint8),
        ("a", np.uint8),
        ("normal", np.float32, (3,)),
        ("position", np.float32, (3,)),
    ]
)
dtype_point_xyz_rgba_label = np.dtype(
    [
        ("position", np.float32, (3,)),
        ("r", np.uint8),
        ("g", np.uint8),
        ("b", np.uint8),
        ("a", np.uint8),
        ("label", np.int32),
    ]
)


dtype_color_to_rgba_dict = {
    dtype_point_color_xyz: dtype_point_rgba_xyz,
    dtype_point_color_normal_xyz: dtype_point_rgba_normal_xyz,
    dtype_point_xyz_color_label: dtype_point_xyz_rgba_label,
}
dtype_rgba_to_color_dict = {v: k for k, v in dtype_color_to_rgba_dict.items()}


def dtype_from_point_type(point_type: PointContentType):
    if point_type == PointContentType.ePoints:
        return dtype_point_xyz
    if point_type == PointContentType.eColoredPoints:
        return dtype_point_color_xyz
    if point_type == PointContentType.eOrientedPoints:
        return dtype_point_normal_xyz
    if point_type == PointContentType.eColoredOrientedPoints:
        return dtype_point_color_normal_xyz
    if point_type == PointContentType.eLabeledPoints:
        return dtype_point_xyz_label
    if point_type == PointContentType.eColoredLabeledPoints:
        return dtype_point_xyz_color_label
    if point_type == PointContentType.eIntensity:
        return dtype_point_xyz_intensity
    raise Exception("PointContentType not yet implemented!", point_type)


def point_type_from_dtype(dt: np.dtype):
    if dt == dtype_point_xyz:
        return PointContentType.ePoints
    if dt == dtype_point_color_xyz:
        return PointContentType.eColoredPoints
    if dt == dtype_point_normal_xyz:
        return PointContentType.eOrientedPoints
    if dt == dtype_point_color_normal_xyz:
        return PointContentType.eColoredOrientedPoints
    if dt == dtype_point_xyz_label:
        return PointContentType.eLabeledPoints
    if dt == dtype_point_xyz_color_label:
        return PointContentType.eColoredLabeledPoints
    if dt == dtype_point_xyz_intensity:
        return PointContentType.eIntensity
    raise Exception("Structured data type not known!", dt)


def get_point_cloud_format(max_points: int, point_dt: np.dtype) -> MetaPointCloudFormat:
    result = MetaPointCloudFormat()
    result.size = max_points * point_dt.itemsize
    result.capacity = result.size
    result.timeProvided = 0
    result.width = max_points
    result.height = 1
    result.type = point_type_from_dtype(point_dt)
    result.seq = 0
    return result


def rgb_to_uint32(r: int, g: int, b: int):
    r, g, b = [np.clip(c, 0, 255) for c in [r, g, b]]
    return r + g * 256 + b * 256 * 256


def uint32_to_rgb(color: int) -> Tuple[int, int, int]:
    r = color % 256
    color //= 256
    g = color % 256
    color //= 256
    b = color % 256
    return r, g, b


def uint32_to_rgb_array(color_array: np.ndarray) -> np.ndarray:
    rgba_dtype = dtype_color_to_rgba_dict[color_array.dtype]
    return color_array.view(rgba_dtype)


def rgb_to_uint32_array(rgba_array: np.ndarray) -> np.ndarray:
    color_dtype = dtype_rgba_to_color_dict[rgba_array.dtype]
    return rgba_array.view(color_dtype)


def crop_by_position(
    pc: np.ndarray,
    crop_min: Tuple[float, float, float],
    crop_max: Tuple[float, float, float],
) -> np.ndarray:
    from functools import reduce

    masks = [
        pc["position"][:, i] >= threshold
        for i, threshold in enumerate(crop_min)
        if threshold is not None
    ]
    masks += [
        pc["position"][:, i] <= threshold
        for i, threshold in enumerate(crop_max)
        if threshold is not None
    ]

    if len(masks) > 0:
        mask = reduce(np.logical_and, masks[1:], masks[0])
        return pc[mask]
    else:
        return pc


def make_pcd_header(
    point_cloud: np.ndarray,
    binary=True,
) -> List[str]:
    """
    Construct lines of a PCD-compatible header.
    :param point_cloud: A point cloud with structured dtype.
    :param binary: Whether point data is stored in binary (True) or ascii (False).
    :return: The lines of the header. If binary, the header is encoded to bytes.
    """

    lines = [
        "VERSION 0.7",
    ]

    fields = ["FIELDS"]
    size = ["SIZE"]
    types = ["TYPE"]
    count = ["COUNT"]

    for name, (dtype, byte_offset) in point_cloud.dtype.fields.items():
        if name == "position":
            assert dtype.shape == (
                3,
            ), f"Expect position dtype to have shape (3,), but got {dtype.shape}."
            assert (
                dtype.base == np.float32
            ), f"Expect position dtype base ot be float32, but got {dtype.base}."
            fields.append("x y z")
        elif name == "color":
            assert (
                dtype.shape == ()
            ), f"Expect color dtype to have shape (), but got {dtype.shape}."
            assert (
                dtype.base == np.uint32
            ), f"Expect position dtype base ot be uint32, but got {dtype.base}."
            fields.append("rgba")
        else:
            raise ValueError(
                f"Encountered unknown field '{name}' of dtype {dtype} in point cloud."
            )

        dim_count = dtype.shape[0] if dtype.shape else 1

        dim_size = dtype.base.itemsize
        dim_type = None
        if np.issubdtype(dtype.base, np.floating):
            dim_type = "F"
        elif np.issubdtype(dtype.base, np.integer):
            if dtype.base.name.startswith("uint"):
                dim_type = "U"
            elif dtype.base.name.startswith("int"):
                dim_type = "I"
        if dim_type is None:
            raise ValueError(
                f"Failed to interpret base {dtype.base} of dtype {dtype} as float, unsigned int or signed int."
            )

        size.append(" ".join(map(str, [dim_size] * dim_count)))
        types.append(" ".join(map(str, [dim_type] * dim_count)))
        count.append(" ".join(map(str, [1] * dim_count)))

    lines += [
        " ".join(fields),
        " ".join(size),
        " ".join(types),
        " ".join(count),
    ]

    if point_cloud.ndim == 2:
        width, height = point_cloud.shape
    else:
        width = point_cloud.size
        height = 1

    lines += [
        f"WIDTH {width}",
        f"HEIGHT {height}",
    ]

    data_format = "binary" if binary else "ascii"
    lines += [
        "VIEWPOINT 0 0 0 1 0 0 0",
        f"POINTS {width * height}",
        f"DATA {data_format}",
    ]

    # Add new lines
    lines = [f"{l}\n" for l in lines]
    if binary:
        lines = [l.encode() for l in lines]

    return lines


def store_point_cloud(
    filepath: str,
    point_cloud: np.ndarray,
):
    """
    Save the point cloud in the binary PCD format [1].

    [1] https://pcl.readthedocs.io/projects/tutorials/en/latest/pcd_file_format.html

    :param filepath: The filepath, used as-is, without adding an extension.
    :param point_cloud: The point cloud data with a structured dtype.
    """
    binary = True  # Non-binary storage is not implemented, yet.

    header_lines = make_pcd_header(point_cloud, binary=binary)

    mode = "wb" if binary else "w"
    with open(filepath, mode) as file:
        # Header
        file.writelines(header_lines)

        # Data
        if binary:
            point_cloud.flatten().view(np.ubyte).tofile(file)
        else:
            raise NotImplementedError(
                "Storing point clouds in non-binary format is not implemented."
            )


def load_point_cloud(
    filepath: str,
) -> np.ndarray:
    """
    Load a point cloud in the binary PCD format [1].

    [1] https://pcl.readthedocs.io/projects/tutorials/en/latest/pcd_file_format.html

    :param filepath: The path to the PCD file.
    :return: The point cloud with a structured dtype.
    """

    with open(filepath, "rb") as file:
        content = file.read()

    # Find end of header
    last_line_of_header = content.find("DATA".encode())
    end_of_header = content.find("\n".encode(), last_line_of_header)

    header = content[:end_of_header]
    data = content[end_of_header + 1 :]

    header_lines: List[str] = header.decode().split("\n")
    header_dict = {}
    for line in header_lines:
        key, value = line.split(" ", maxsplit=1)
        header_dict[key] = value

    known_fields = {
        "rgba": ("color", np.uint32),
        "x y z": ("position", np.float32, (3,)),
    }

    width, height = map(int, [header_dict["WIDTH"], header_dict["HEIGHT"]])
    fields: str = header_dict["FIELDS"]

    dtype_entries = []
    while len(fields) > 0:
        found = False
        for field, dtype_entry in known_fields.items():
            if fields.startswith(field):
                found = True
                # Remove entry.
                fields = fields[len(field) :].strip()
                # Handle
                dtype_entries.append(dtype_entry)

        if not found:
            raise ValueError(
                "Failed to interpret fields '" + header_dict["FIELDS"] + "'."
            )
    dtype = np.dtype(dtype_entries)

    array = np.frombuffer(data, dtype=dtype)

    if height > 1:
        array = array.reshape((width, height))

    return array
