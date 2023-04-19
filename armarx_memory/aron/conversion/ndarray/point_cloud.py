import numpy as np
import typing as ty


class PointCloudConversions:

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
        pcl_dtype = PointCloudConversions.dtype_from_point_type_string(type_str)
        assert pcl_dtype.itemsize == bytes_per_element, f"{pcl_dtype.itemsize} == {bytes_per_element}"

        array: np.ndarray = np.frombuffer(buffer=byte_data, dtype=pcl_dtype)
        array = array.reshape(shape)
        assert array.shape == shape, f"{array.shape} == {shape}"

        point_cloud = PointCloudConversions.point_cloud_without_paddings(array)
        return point_cloud
