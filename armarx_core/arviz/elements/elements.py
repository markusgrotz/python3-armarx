import enum
from typing import Dict, Tuple

import numpy as np


import armarx.viz as viz
from armarx.arviz import conversions
from armarx.arviz.elements.Element import Element


def direction_to_ori_mat(dir: np.ndarray, natural_dir=(0, 1, 0)) -> np.ndarray:
    import transforms3d as tf3d

    dir = np.array(dir)
    dir /= np.linalg.norm(dir)
    cross = np.cross(natural_dir, dir)
    angle = np.arccos(natural_dir.dot(dir))
    if np.linalg.norm(angle) < 1e-6:
        # Directions are almost colinear => Do no rotation
        cross = np.array((1, 0, 0))
        angle = 0.0
    axis = cross / np.linalg.norm(cross)
    ori = tf3d.axangles.axangle2mat(axis, angle)
    return ori


class Arrow(Element):
    """
    An arrow.
    """

    natural_dir = np.array((0, 1, 0))

    def __init__(
        self,
        id,
        length=100.0,
        width=10.0,
        direction=None,
        from_to=None,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementArrow, id=id, **kwargs)
        self.length: float = length
        self.width: float = width
        if direction is not None:
            self.direction = direction
        if from_to is not None:
            self.from_to = from_to

    @property
    def direction(self):
        return self.ori_mat @ self.natural_dir

    @direction.setter
    def direction(self, value):
        self.ori_mat = direction_to_ori_mat(value, self.natural_dir)

    @property
    def from_to(self):
        return self.position, self.position + self.length * self.direction

    @from_to.setter
    def from_to(self, value):
        start, end = value
        self.position = start
        dir = end - self.position
        norm = np.linalg.norm(dir)
        self.direction = dir / norm
        self.length = norm

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data.length = float(self.length)
        ice_data.width = float(self.width)


class ArrowCircle(Element):
    """
    An arrow circle.
    """

    natural_normal = np.array((0, 1, 0))

    def __init__(
        self,
        id,
        radius=100.0,
        completion=1.0,
        width=10.0,
        normal=None,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementArrowCircle, id=id, **kwargs)
        self.radius: float = radius
        self.completion: float = completion
        self.width: float = width
        if normal is not None:
            self.normal = normal

    @property
    def normal(self) -> np.ndarray:
        return self.ori_mat @ self.natural_normal

    @normal.setter
    def normal(self, value):
        self.ori_mat = direction_to_ori_mat(value, self.natural_normal)

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data.radius = float(self.radius)
        ice_data.completion = float(self.completion)
        ice_data.width = float(self.width)


class Box(Element):
    """
    A box.
    """

    def __init__(
        self,
        id,
        size=1.0,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementBox, id=id, **kwargs)

        self.size = size

    @property
    def size(self) -> np.ndarray:
        return self._size

    @size.setter
    def size(self, value):
        try:
            iter(value)
            value = self._to_array_checked(value, (3,), "size vector", np.float)
            self._size = value
        except TypeError:
            self._size = np.array([value, value, value]).astype(np.float)

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data.size = conversions.vector3f_from_numpy(self.size)


class Cylinder(Element):
    """
    A cylinder.
    """

    natural_dir = np.array((0, 1, 0))

    def __init__(
        self,
        id,
        radius=10.0,
        height=10.0,
        direction=None,
        from_to=None,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementCylinder, id=id, **kwargs)
        self.radius: float = radius
        self.height: float = height

        if direction is not None:
            self.direction = direction
        if from_to is not None:
            self.from_to = from_to

    @property
    def from_to(self):
        pos = self.position
        dir = self.direction
        return pos - self.height / 2 * dir, pos + self.height / 2 * dir

    @from_to.setter
    def from_to(self, value):
        start, end = value
        start, end = np.array(start), np.array(end)
        self.position = 0.5 * (start + end)
        direction = end - start
        self.direction = direction
        self.height = np.linalg.norm(direction)

    @property
    def direction(self):
        return self.ori_mat @ self.natural_dir

    @direction.setter
    def direction(self, value):
        self.ori_mat = direction_to_ori_mat(value, self.natural_dir)

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data.radius = self.radius
        ice_data.height = self.height


class Sphere(Element):
    """
    A sphere.
    """

    def __init__(
        self,
        id,
        radius=10.0,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementSphere, id=id, **kwargs)
        self.radius: float = radius

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data.radius = float(self.radius)


class Ellipsoid(Element):
    """
    An ellipsoid.
    """

    def __init__(
        self,
        id,
        axis_lengths=None,
        curvature=None,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementEllipsoid, id=id, **kwargs)

        self.axis_lengths = (1, 1, 1) if axis_lengths is None else axis_lengths
        self.curvature = (0, 0, 0) if curvature is None else curvature

    @property
    def axis_lengths(self) -> np.ndarray:
        return self._axis_lengths

    @axis_lengths.setter
    def axis_lengths(self, value):
        try:
            iter(value)
            value = self._to_array_checked(
                value, (3,), "ellipsoid axis lengths", np.float
            )
            self._axis_lengths = value
        except TypeError:
            self._axis_lengths = np.array([value, value, value]).astype(np.float)

    @property
    def curvature(self) -> np.ndarray:
        return self._curvature

    @curvature.setter
    def curvature(self, value):
        value = self._to_array_checked(value, (3,), "curvature", np.float)
        self._curvature = value

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data.axisLengths = conversions.vector3f_from_numpy(self.axis_lengths)
        ice_data.curvature = conversions.vector3f_from_numpy(self.curvature)


class Line(Element):
    """
    A line.
    """

    def __init__(
        self,
        id,
        start=None,
        end=None,
        line_width=10.0,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementLine, id=id, **kwargs)

        self.line_width: float = line_width

        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

    @property
    def start(self) -> np.ndarray:
        return self._start

    @start.setter
    def start(self, value):
        value = self._to_array_checked(value, (3,), "start position")
        self._start = value

    @property
    def end(self) -> np.ndarray:
        return self._end

    @end.setter
    def end(self, value):
        value = self._to_array_checked(value, (3,), "start position")
        self._end = value

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data._from = conversions.vector3f_from_numpy(self.start)
        ice_data.to = conversions.vector3f_from_numpy(self.end)


class Pose(Element):
    """
    A 6-D pose.
    """

    def __init__(
        self,
        id,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementPose, id=id, **kwargs)


class Text(Element):
    def __init__(
        self,
        id,
        text="",
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementText, id=id, **kwargs)
        self.text: str = text

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data.text = str(self.text)


class ModelDrawStyle(enum.IntFlag):
    ORIGINAL = 0
    COLLISION = 1
    OVERRIDE_COLOR = 2


class Object(Element):
    def __init__(
        self,
        id,
        project="",
        filename="",
        file=None,
        use_collision_model=False,
        override_color=None,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementObject, id=id, **kwargs)
        self.project: str = project
        self.filename: str = filename
        self.draw_style: ModelDrawStyle = ModelDrawStyle.ORIGINAL

        if file is not None:
            self.file = file

        if use_collision_model:
            self.use_collision_model()
        if override_color is not None:
            self.override_color(override_color)

    @property
    def file(self) -> Tuple[str, str]:
        return self.project, self.filename

    @file.setter
    def file(self, value):
        self.project, self.filename = value

    @property
    def draw_style(self) -> ModelDrawStyle:
        return self._draw_style

    @draw_style.setter
    def draw_style(self, value):
        self._draw_style = ModelDrawStyle(value)

    def use_collision_model(self):
        self.draw_style |= ModelDrawStyle.COLLISION

    def use_full_model(self):
        self.draw_style &= ~ModelDrawStyle.COLLISION

    def override_color(self, color):
        self.draw_style |= ModelDrawStyle.OVERRIDE_COLOR
        self.color = color

    def use_original_color(self):
        self.draw_style &= ~ModelDrawStyle.OVERRIDE_COLOR

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data.project = str(self.project)
        ice_data.filename = str(self.filename)
        ice_data.drawStyle = int(self.draw_style)


class Robot(Object):
    """
    A robot.
    """

    def __init__(
        self,
        id,
        joint_angles=None,
        **kwargs,
    ):
        super().__init__(id=id, **kwargs)
        self.ice_data_cls = viz.data.ElementRobot

        self.joint_angles: Dict[str, float] = (
            {} if joint_angles is None else joint_angles
        )

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data.jointValues = self.joint_angles


class PointCloud(Element):
    """
    A point cloud.
    """

    def __init__(
        self,
        id,
        transparency=0.0,
        point_size=1.0,
        points=None,
        point_colors=None,
        **kwargs,
    ):
        """
        :param id:
        :param transparency:
        :param point_size: The point size in pixels.
        :param points:
        :param point_colors:
        :param kwargs:
        """
        super().__init__(ice_data_cls=viz.data.ElementPointCloud, id=id, **kwargs)
        self.points = np.zeros((0, 7))

        self.transparency: float = transparency
        self.point_size: float = point_size

        if points is not None:
            self.points = points
        if point_colors is not None:
            self.point_colors = point_colors

    def clear(self):
        self.points = []

    @property
    def points(self) -> np.ndarray:
        """
        An array of shape (N, 7) containing N points of the form (x, y, z, r, g, b, a),
        or an empty array if there are no points.
        """
        return self._points

    @points.setter
    def points(self, value):
        """
        :param value:
        An array-like of one of the following shapes:
            (N, 3): Set as (x, y, z) with default color (100, 100, 100, 255).
            (N, 6): Set as (x, y, z, r, g, b) with default alpha (255).
            (N, 7): Set as (x, y, z, r, g, b, a).
        """
        value = self._to_array_checked(
            value, [(0,), (None, 3), (None, 6), (None, 7)], "points", dtype=np.float
        )
        if value.size == 0:
            self._points = value
            return

        self._points = np.stack([[0, 0, 0, 100, 100, 100, 255]] * value.shape[0])
        self._points[:, : value.shape[-1]] = value

    @property
    def point_positions(self) -> np.ndarray:
        """An N x 3 slice of `self.points` containing the point positions as (x, y, z)."""
        return self._points[:, :3]

    @point_positions.setter
    def point_positions(self, value):
        value = self._to_array_checked(
            value, [(None, 3)], "point positions", dtype=np.float
        )
        self._points[:, :3] = value

    @property
    def point_colors(self) -> np.ndarray:
        """An N x 4 slice of `self.points` containing the point colors as (r, g, b, a)."""
        return self._points[:, 3:]

    @point_colors.setter
    def point_colors(self, value):
        value = self._to_array_checked(
            value, [(3,), (4,), (None, 3), (None, 4)], "point colors"
        )
        self._points[:, 3 : (3 + value.shape[-1])] = value

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)

        dtype = np.dtype(
            [
                ("position", np.float32, (3,)),
                ("a", np.uint8),
                ("r", np.uint8),
                ("g", np.uint8),
                ("b", np.uint8),
            ]
        )
        buffer = np.zeros(self.points.shape[0], dtype=dtype)

        assert self.points.shape[1] == 7
        buffer["position"] = self.points[:, :3]
        buffer["r"] = self.points[:, 3]
        buffer["g"] = self.points[:, 4]
        buffer["b"] = self.points[:, 5]
        buffer["a"] = self.points[:, 6]

        ice_data.points = buffer
        ice_data.transparency = self.transparency
        ice_data.point_size = self.point_size


class Polygon(Element):
    """
    A polygon.
    """

    def __init__(
        self,
        id,
        line_width=0.0,
        line_color=None,
        points=None,
        **kwargs,
    ):
        super().__init__(ice_data_cls=viz.data.ElementPolygon, id=id, **kwargs)
        self.points = []

        self.line_width: float = line_width
        self.line_color = line_color if line_color is not None else (100, 100, 100, 255)

        if points is not None:
            self.points = points

    @property
    def line_color(self) -> np.ndarray:
        """
        The line color of the polygon
        """
        return self._line_color

    @line_color.setter
    def line_color(self, value):
        value = self._to_array_checked(value, [(3,), (4,)], "line color")
        if value.shape == (3,):
            self._line_color = np.concatenate([value, [255]])
        else:
            self._line_color = value

    def clear(self):
        self.points = []

    @property
    def points(self) -> np.ndarray:
        return self._points

    @points.setter
    def points(self, value):
        value = self._to_array_checked(
            value, [(0,), (None, 3)], "polygon points", dtype=np.float
        )
        self._points = value

    def _update_ice_data(self, ice_data):
        super()._update_ice_data(ice_data)
        ice_data.line_width = float(self.line_width)
        ice_data.line_color = conversions.to_viz_color(self.color)
        ice_data.points = conversions.vector3fs_from_numpy(self.points)
