"""
Module for to interact with objects
"""

import os
import time

from typing import List

import numpy as np

from armarx.pose_helper import pose2mat
from armarx.pose_helper import mat2pose

from armarx.ice_manager import get_proxy
from armarx.ice_manager import get_topic
from armarx.slice_loader import load_armarx_slice

load_armarx_slice("RobotAPI", "objectpose/ObjectPoseProvider.ice")
load_armarx_slice("RobotAPI", "objectpose/ObjectPoseStorageInterface.ice")


from armarx.objpose import ObjectPoseStorageInterfacePrx

from armarx.objpose.data import ProvidedObjectPose
from armarx.objpose import ObjectPoseProviderPrx
from armarx.objpose import ObjectPoseTopicPrx

from armarx.data import ObjectID


def provide_poses(
    provider_name: str,
    object_names: List[str],
    poses: List[np.ndarray],
    timestamp: int = None,
):
    """
    Writes object poses to the memory

    :param provider_name: name of the provider
    :param object_name: list of object names
    :param poses: list of object poses
    """
    pose_topic = get_topic(ObjectPoseTopicPrx, "ObjectPoseTopic")
    object_poses = []
    for name, pose in zip(object_names, poses):
        pose = mat2pose(pose)
        timestamp = timestamp or (time.time() * 1e6)
        dataset, object_name = name.split("/")
        object_id = ObjectID(dataset, object_name, object_name)
        object_pose = ProvidedObjectPose(
            providerName=provider_name,
            objectPose=pose,
            objectID=object_id,
            timestampMicroSeconds=timestamp,
        )
        object_poses.append(object_pose)
    pose_topic.reportObjectPoses(provider_name, object_poses)


def get_object_poses():
    """
    Reads object poses from the robot's memory
    """
    object_memory = get_proxy(ObjectPoseStorageInterfacePrx, "ObjectMemory")
    object_poses = object_memory.getObjectPoses()
    object_poses = {o.objectID.className: o for o in object_poses}

    return {
        object_name: {
            "pose": pose2mat(object_info.objectPoseOriginal),
            "timestamp": object_info.timestamp.timeSinceEpoch.microSeconds / 1e6,
            "provider_name": object_info.providerName,
            "confidence": object_info.confidence,
            "dataset": object_info.objectID.dataset,
        }
        for object_name, object_info in object_poses.items()
    }


def get_object_path(
    database: str = "Kitchen", object_name: str = "vitalis_cereal", suffix: str = "obj"
):
    """
    Returns the file path for an object from the object database
    """
    data_path = os.environ.get(
        "h2t__PriorKnowledgeData__PATH", "./code/h2t/PriorKnowledgeData/"
    )
    if not os.path.exists(data_path):
        return None
    data_path = os.path.join(data_path, "data/PriorKnowledgeData/objects")
    data_path = os.path.join(
        data_path, database, object_name, f"{object_name}.{suffix}"
    )
    return data_path
