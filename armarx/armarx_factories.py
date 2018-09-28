import Ice

from .interface_helper import load_armarx_slice, ice_communicator
load_armarx_slice('RobotAPI', 'observers/KinematicUnitObserverInterface.ice')

from armarx import DatafieldRefBase
from armarx import ChannelRefBase

from .variants import Variant
from .variants import TimedVariant


class VariantFactory(Ice.ObjectFactory):
    def create(self, t):
        return Variant()


class TimedVariantFactory(Ice.ObjectFactory):
    def create(self, t):
        return TimedVariant()


class DatafieldRef(DatafieldRefBase):
    pass


class DatafieldRefFactory(Ice.ObjectFactory):
    def create(self, t):
        return DatafieldRef()


class ChannelRef(ChannelRefBase):
    pass


class ChannelRefFactory(Ice.ObjectFactory):
    def create(self, t):
        return ChannelRef()


load_armarx_slice('RobotAPI', 'core/FramedPoseBase.ice')
from armarx import PoseBase
from armarx import FramedPositionBase
from armarx import FramedPoseBase
from armarx import Vector3Base
from armarx import QuaternionBase

load_armarx_slice('ArmarXCore', 'observers/Timestamp.ice')
from armarx import TimestampBase


class Vector3(Vector3Base):
        pass

class Vector3Factory(Ice.ObjectFactory):
    def create(self, t):
        return Vector3()

class Quaternion(QuaternionBase):
        pass

class QuaternionFactory(Ice.ObjectFactory):
    def create(self, t):
        return Quaternion()


class Pose(PoseBase):
    pass

class PoseFactory(Ice.ObjectFactory):
    def create(self, t):
        return Pose()


class FramedPosition(FramedPositionBase):
        pass

class FramedPositionFactory(Ice.ObjectFactory):
    def create(self, t):
        return FramedPosition()


class FramedPose(FramedPoseBase):
        pass

class FramedPoseFactory(Ice.ObjectFactory):
    def create(self, t):
        return FramedPose()


class Timestamp(TimestampBase):
        pass

class TimestampFactory(Ice.ObjectFactory):
    def create(self, t):
        return Timestamp()



load_armarx_slice('MemoryX', 'components/WorkingMemoryInterface.ice')
from memoryx import SegmentLockBase
from memoryx import EntityAttributeBase
from memoryx import PlanePrimitiveBase

class SegmentLock(SegmentLockBase):
    pass


class SegmentLockFactory(Ice.ObjectFactory):
    def create(self, t):
        return SegmentLock()


class EntityAttribute(EntityAttributeBase):
    pass


class EntityAttributeFactory(Ice.ObjectFactory):
    def create(self, t):
        return EntityAttribute()


class PlanePrimitive(PlanePrimitiveBase):
    pass


class PlanePrimitiveFactory(Ice.ObjectFactory):
    def create(self, t):
        return PlanePrimitive()


def register():
    ice_communicator.addObjectFactory(VariantFactory(), Variant.ice_staticId())
    ice_communicator.addObjectFactory(TimedVariantFactory(), TimedVariant.ice_staticId())
    ice_communicator.addObjectFactory(DatafieldRefFactory(), DatafieldRef.ice_staticId())
    ice_communicator.addObjectFactory(ChannelRefFactory(), ChannelRef.ice_staticId())

    ice_communicator.addObjectFactory(TimestampFactory(), Timestamp.ice_staticId())
    ice_communicator.addObjectFactory(Vector3Factory(), Vector3.ice_staticId())
    ice_communicator.addObjectFactory(QuaternionFactory(), Quaternion.ice_staticId())
    ice_communicator.addObjectFactory(PoseFactory(), Pose.ice_staticId())
    ice_communicator.addObjectFactory(FramedPositionFactory(), FramedPosition.ice_staticId())
    ice_communicator.addObjectFactory(FramedPoseFactory(), FramedPose.ice_staticId())

    ice_communicator.addObjectFactory(SegmentLockFactory(), SegmentLock.ice_staticId())
    ice_communicator.addObjectFactory(EntityAttributeFactory(), EntityAttribute.ice_staticId())
    ice_communicator.addObjectFactory(PlanePrimitiveFactory(), PlanePrimitive.ice_staticId())
