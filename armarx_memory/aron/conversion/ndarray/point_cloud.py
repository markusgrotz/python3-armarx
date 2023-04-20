import numpy as np
import typing as ty

from armarx_memory.aron.aron_ice_types import AronIceTypes


class PointCloudConversions:

    dtype_point_color_xyz = np.dtype([
        ("position", np.float32, (4,)),  # 4 * 4 = 16
        ("color", np.uint32),  # 1 x 4 = 4
        ("padding", np.uint8, (12,)),  # 12 x 1 = 12
    ])  # 32 bytes in total

    dtype_point_xyz_color_label = np.dtype([
        ("position", np.float32, (4,)),  # 4 * 4 = 16
        ("color", np.uint32),  # 1 x 4 = 4
        ("label", np.uint32),  # 1 x 4 = 4
        ("padding", np.uint8, (8,)),  # 8 x 1 = 8
    ])  # 32 bytes in total


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
    def dtype_to_point_type_string(cls, dtype: np.dtype) -> str:
        suffix = cls.dtype_to_point_type_string_dict.get(dtype, None)

        if suffix is None:
            fields = dtype.fields
            # Determine from dtype fields.
            assert "position" in fields, fields
            if "color" in fields:
                if "label" in fields:
                    suffix = "XYZRGBL"
                else:
                    suffix = "XYZRGBA"
            else:
                if "label" in fields:
                    suffix = "XYZL"
                else:
                    suffix = "XYZ"

        return f"pcl::Point{suffix}"

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
    def point_cloud_without_paddings(cls, pcl_point_cloud: np.ndarray) -> np.ndarray:
        # Remove paddings to dtypes defined for point cloud providers/processors.
        py_dtype = cls.dtype_without_paddings(pcl_point_cloud.dtype)
        py_point_cloud = np.zeros(pcl_point_cloud.shape, dtype=py_dtype)
        for key in py_point_cloud.dtype.fields:
            if key == "position":
                py_point_cloud[key] = pcl_point_cloud[key][..., :3]
            else:
                py_point_cloud[key] = pcl_point_cloud[key]

        return py_point_cloud

    @classmethod
    def point_cloud_with_paddings(
            cls,
            py_point_cloud: np.ndarray,
            pcl_dtype,
    ) -> np.ndarray:
        # Add paddings to dtypes defined for point cloud providers/processors.
        pcl_point_cloud = np.zeros(py_point_cloud.shape, dtype=pcl_dtype)
        for key in pcl_point_cloud.dtype.fields:
            if key == "position":
                pcl_point_cloud[key][..., :3] = py_point_cloud[key]
            elif key == "padding":
                pass
            else:
                pcl_point_cloud[key] = py_point_cloud[key]

        return pcl_point_cloud

    @classmethod
    def pcl_point_cloud_to_py_point_cloud(
            cls,
            byte_data: bytes,
            type_str: str,
            shape: ty.Tuple,
            bytes_per_element: int,
    ):
        pcl_dtype = cls.dtype_from_point_type_string(type_str)
        assert pcl_dtype.itemsize == bytes_per_element, f"{pcl_dtype.itemsize} == {bytes_per_element}"

        pcl_array: np.ndarray = np.frombuffer(buffer=byte_data, dtype=pcl_dtype)
        pcl_array = pcl_array.reshape(shape)
        assert pcl_array.shape == shape, f"{pcl_array.shape} == {shape}"

        py_point_cloud = cls.point_cloud_without_paddings(pcl_array)
        return py_point_cloud

    @classmethod
    def pcl_point_cloud_from_py_point_cloud(
            cls,
            py_point_cloud: np.ndarray,
    ):
        type_string = cls.dtype_to_point_type_string(py_point_cloud.dtype)
        pcl_dtype = cls.dtype_from_point_type_string(type_string)

        # Add paddings to match PCL byte alignment.
        pcl_point_cloud = cls.point_cloud_with_paddings(py_point_cloud, pcl_dtype)

        shape = (*pcl_point_cloud.shape, pcl_point_cloud.itemsize)
        return AronIceTypes.NDArray(
            shape=shape,
            type=type_string,
            data=pcl_point_cloud.tobytes(),
        )
