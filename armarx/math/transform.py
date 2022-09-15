from typing import Iterable, Union, List

import numpy as np


class Transform:
    def __init__(
        self,
        transform=None,
        translation=None,
        rotation=None,
    ):

        self.transform = np.eye(4)
        if transform is not None:
            self.transform = transform
        if translation is not None:
            self.translation = translation
        if rotation is not None:
            self.rotation = rotation

    @property
    def transform(self) -> np.ndarray:
        """The transform as 4x4 transformation matrix."""
        return self._transform

    @transform.setter
    def transform(self, value):
        value = self._to_array_checked(
            value, (4, 4), "transform matrix", dtype=np.float
        )
        self._transform = value

    @property
    def translation(self) -> np.ndarray:
        return self._transform[:3, 3]

    @translation.setter
    def translation(self, value):
        value = self._to_array_checked(
            value, [(3,), (3, 1)], "translation vector", dtype=np.float
        )
        self._transform[:3, 3] = value

    @property
    def rotation(self):
        return self.rot_mat

    @rotation.setter
    def rotation(self, value):
        value = np.array(value)
        if value.shape == (4,):
            self.rot_quat = value
        elif value.shape == (3, 3):
            self.rot_mat = value
        else:
            raise ValueError(f"Invalid rotation value: {value}")

    @property
    def rot_mat(self) -> np.ndarray:
        """The rotation as 3x3 rotation matrix."""
        return self._transform[:3, :3]

    @rot_mat.setter
    def rot_mat(self, value):
        """Set the rotation as 3x3 rotation matrix."""
        value = self._to_array_checked(value, (3, 3), "rotation matrix", dtype=np.float)
        self._transform[:3, :3] = value

    @property
    def rot_quat(self):
        """The rotation as [w, x, y, z] quaternion."""
        import transforms3d as tf3d

        try:
            return tf3d.quaternions.mat2quat(self.rot_mat)
        except np.linalg.LinAlgError as e:
            print("Rotation matrix to quaternion: \n{}".format(self.rot_mat))
            raise

    @rot_quat.setter
    def rot_quat(self, value):
        import transforms3d as tf3d

        try:
            self.rot_mat = tf3d.quaternions.quat2mat(value)
        except np.linalg.LinAlgError as e:
            print("Quaternion to rotation matrix: \n{}".format(value))
            raise

    def inverted(self) -> "Transform":
        """
        Return the inverted transform of self.
        :return: self^(-1)
        """
        return Transform(
            rotation=self.rot_mat.T, translation=-self.rot_mat.T @ self.translation
        )

    def __mul__(self, other: "Transform"):
        """
        Return (self * other) with * being the matrix multiplication.
        :param other: Another transform.
        :return: self * other
        """
        if not isinstance(other, Transform):
            raise TypeError(
                f"Unsupported operator * between {type(self)} and {type(other)}."
            )
        return Transform(self.transform @ other.transform)

    def is_close_to(self, other: "Transform", **kwargs):
        """
        Return true of other is close to self.
        :param other: Another transform.
        :param kwargs: Keyword arguments passed to np.allclose()
        :return: self == other
        """
        return np.allclose(self.transform, other.transform, **kwargs)

    @classmethod
    def _match_shape(
        cls, shape: Iterable[int], shape_pattern: Iterable[Union[int, None]]
    ):
        """
        Indicate whether `shape` matches `accepted_shape`.
        :param shape: An array shape, i.e. tuple of ints.
        :param shape_pattern:
            A shape pattern, i.e. tuple of ints or None, where None matches any size.
        :return: True if `shape` matches `accepted_shape`.
        """
        return np.all(
            np.logical_or(
                np.array(shape) == shape_pattern,
                np.isnan(np.array(shape_pattern, dtype=np.float)),
            )
        )

    @classmethod
    def _match_shapes(
        cls, shape: Iterable[int], shape_patterns: List[Iterable[Union[int, None]]]
    ):
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
                shape_str = " or ".join(
                    [
                        ", ".join(map(cls._shape_to_str, accepted_shapes[:-1])),
                        cls._shape_to_str(accepted_shapes[-1]),
                    ]
                )
            raise ValueError(
                f"Expected {name} of shape {shape_str}, but got array of shape {value.shape}."
            )
        return value
