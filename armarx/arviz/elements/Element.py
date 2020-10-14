import enum
from typing import Iterable, Union, List

import numpy as np


class ElementFlags(enum.IntFlag):
    NONE = 0
    OVERRIDE_MATERIAL = 1
    HIDDEN = 2


class Element:

    def __init__(self, ice_data_cls, id,
                 pose=None, position=None, orientation=None,
                 color=None, scale=1.0):
        self.ice_data_cls = ice_data_cls
        self.id: str = str(id)

        self.pose = np.eye(4)
        if pose is not None:
            self.pose = pose
        if position is not None:
            self.position = position
        if orientation is not None:
            self.ori_mat = orientation

        self.color = color if color is not None else (100, 100, 100, 255)

        self.scale: float = scale
        self.flags: ElementFlags = ElementFlags.NONE

    @property
    def pose(self) -> np.ndarray:
        """The pose as 4x4 transformation matrix."""
        return self._pose

    @pose.setter
    def pose(self, value):
        value = self._to_array_checked(value, (4, 4), "pose matrix", dtype=np.float)
        self._pose = value

    @property
    def position(self) -> np.ndarray:
        return self._pose[:3, 3]

    @position.setter
    def position(self, value):
        value = self._to_array_checked(value, [(3,), (3, 1)], "position vector", dtype=np.float)
        self._pose[:3, 3] = value

    @property
    def orientation(self):
        return self.ori_mat

    @orientation.setter
    def orientation(self, value):
        value = np.array(value)
        if value.shape == (4,):
            self.ori_quat = value
        elif value.shape == (3, 3):
            self.ori_mat = value
        else:
            raise ValueError("Invalid orientation value: {}".format(value))

    @property
    def ori_mat(self) -> np.ndarray:
        """The orientation as 3x3 rotation matrix."""
        return self._pose[:3, :3]

    @ori_mat.setter
    def ori_mat(self, value):
        """Set the orientation as 3x3 rotation matrix."""
        value = self._to_array_checked(value, (3, 3), "orientation matrix", dtype=np.float)
        self._pose[:3, :3] = value

    @property
    def ori_quat(self):
        """The orientation as [w, x, y, z] quaternion."""
        import transforms3d as tf3d
        try:
            return tf3d.quaternions.mat2quat(self.ori_mat)
        except np.linalg.LinAlgError as e:
            print("Rotation matrix to quaternion: \n{}".format(self.ori_mat))
            raise

    @ori_quat.setter
    def ori_quat(self, value):
        import transforms3d as tf3d
        try:
            self.ori_mat = tf3d.quaternions.quat2mat(value)
        except np.linalg.LinAlgError as e:
            print("Quaternion to rotation matrix: \n{}".format(value))
            raise

    @property
    def color(self) -> np.ndarray:
        return self._color

    @color.setter
    def color(self, value):
        value = self._to_array_checked(value, [(3,), (4,)], "color")
        if value.shape == (3,):
            self._color = np.concatenate([value, [255]])
        else:
            self._color = value

    def get_ice_data(self):
        """Get the Ice data for committing."""
        ice_data = self.ice_data_cls(id=self.id)
        self._update_ice_data(ice_data)
        return ice_data

    def _update_ice_data(self, ice_data):
        """
        Update the given element data with self's values.
        :param data: armarx.viz.data.Element
        """
        p = ice_data.pose
        p.x, p.y, p.z = self.position
        p.qw, p.qx, p.qy, p.qz = map(float, self.ori_quat)

        c = ice_data.color
        c.r, c.g, c.b, c.a = map(int, self.color)
        ice_data.scale = float(self.scale)
        ice_data.flags = int(self.flags)


    @classmethod
    def _match_shape(cls, shape: Iterable[int], shape_pattern: Iterable[Union[int, None]]):
        """
        Indicate whether `shape` matches `accepted_shape`.
        :param shape: An array shape, i.e. tuple of ints.
        :param shape_pattern: 
            A shape pattern, i.e. tuple of ints or None, where None matches any size.
        :return: True if `shape` matches `accepted_shape`. 
        """
        return np.all(np.logical_or(np.array(shape) == shape_pattern,
                                    np.isnan(np.array(shape_pattern, dtype=np.float))))

    @classmethod
    def _match_shapes(cls, shape: Iterable[int], shape_patterns: List[Iterable[Union[int, None]]]):
        for pattern in shape_patterns:
            if cls._match_shape(shape, pattern):
                return True
        return False

    @classmethod
    def _shape_to_str(cls, shape):
        return "({})".format(", ".join(["N" if c is None else str(c) for c in shape]))

    @classmethod
    def _to_array_checked(cls, value, accepted_shapes, name, dtype=None) -> np.ndarray:
        assert len(accepted_shapes) > 0
        value = np.array(value)
        if dtype is not None:
            value = value.astype(dtype)
        if isinstance(accepted_shapes, tuple):
            accepted_shapes = [accepted_shapes]

        if not cls._match_shapes(value.shape, accepted_shapes):
            if len(accepted_shapes) == 1:
                shape_str = cls._shape_to_str(accepted_shapes[0])
            else:
                shape_str = " or ".join([", ".join(map(cls._shape_to_str, accepted_shapes[:-1])),
                                         cls._shape_to_str(accepted_shapes[-1])])
            raise ValueError("Expected {} of shape {}, but got array of shape {}.".format(
                name, shape_str, value.shape))
        return value

