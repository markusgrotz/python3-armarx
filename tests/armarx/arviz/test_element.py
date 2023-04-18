import pytest

import numpy as np
import transforms3d as tf3d

import armarx
import armarx_core.arviz as viz


@pytest.fixture
def element():
    from armarx_core.arviz.elements import Element

    e = Element(armarx.viz.data.ElementPose, "id")
    return e


def check_position(e, pos):
    assert np.array_equal(e.pose[:3, 3], pos)
    assert np.array_equal(e.position, pos)


def check_orientation(e, ori_mat=None, ori_quat=None):
    assert not (
        ori_mat is None and ori_quat is None
    ), "Either ori_mat or ori_quat must be given."
    if ori_mat is None:
        ori_mat = tf3d.quaternions.quat2mat(ori_quat)
    elif ori_quat is None:
        ori_quat = tf3d.quaternions.mat2quat(ori_mat)

    assert np.array_equal(e.pose[:3, :3], ori_mat)
    assert np.array_equal(e.orientation, ori_mat)
    assert np.array_equal(e.ori_mat, ori_mat)
    assert np.array_equal(e.ori_quat, ori_quat)


def test_element_position_default(element):
    check_position(element, np.zeros(3))


def test_element_position_set_pose(element):
    pos = (1, 2, 3)
    pose = np.eye(4)
    pose[:3, 3] = pos
    element.pose = pose
    check_position(element, pos)


def test_element_position_set_pose_submatrix(element):
    pos = (1, 2, 3)
    element.pose[:3, 3] = pos
    check_position(element, pos)


def test_element_position_set_position(element):
    pos = (1, 2, 3)
    element.position = pos
    check_position(element, pos)


def test_element_orientation_default(element):
    check_orientation(element, ori_mat=np.eye(3), ori_quat=tf3d.quaternions.qeye())


def test_element_orientation_set_pose(element):
    ori_mat = tf3d.axangles.axangle2mat([0, 1, 0], np.pi)
    pose = np.eye(4)
    pose[:3, :3] = ori_mat
    element.pose = pose
    check_orientation(element, ori_mat=ori_mat)


def test_element_orientation_set_pose_submatrix(element):
    ori_mat = tf3d.axangles.axangle2mat([0, 1, 0], np.pi)
    element.pose[:3, :3] = ori_mat
    check_orientation(element, ori_mat=ori_mat)


def test_element_orientation_set_orientation_mat(element):
    ori_mat = tf3d.axangles.axangle2mat([0, 1, 0], np.pi)
    element.orientation = ori_mat
    check_orientation(element, ori_mat=ori_mat)


def test_element_orientation_set_orientation_quat(element):
    ori_quat = tf3d.quaternions.axangle2quat([0, 1, 0], np.pi)
    element.orientation = ori_quat
    check_orientation(element, ori_quat=ori_quat)


def test_element_orientation_set_ori_quat(element):
    ori_quat = tf3d.quaternions.axangle2quat([0, 1, 0], np.pi)
    element.ori_quat = ori_quat
    check_orientation(element, ori_quat=ori_quat)
