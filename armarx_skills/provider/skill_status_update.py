import enum

import dataclasses as dc
import typing as ty

from armarx_memory.ice_conv.ice_converter import IceConverter
from armarx_memory.aron.conversion import pythonic_from_to_aron_ice as aron_conv
from armarx_skills.provider import dto
from armarx_skills.provider.skill_id import SkillID, SkillIdConv
from armarx_skills.callback import dti as callback_dti


class ExecutionStatus(enum.Enum):
    Idle = enum.auto()
    Scheduled = enum.auto()
    Running = enum.auto()

    Failed = enum.auto()
    Succeeded = enum.auto()
    Aborted = enum.auto()


class ExecutionStatusConv(IceConverter):

    def __init__(self):
        super().__init__()
        self.py_to_ice_map = {
            ExecutionStatus.Idle: dto.Status.Idle,
            ExecutionStatus.Scheduled: dto.Status.Scheduled,
            ExecutionStatus.Running: dto.Status.Running,
            ExecutionStatus.Failed: dto.Status.Failed,
            ExecutionStatus.Succeeded: dto.Status.Succeeded,
            ExecutionStatus.Aborted: dto.Status.Aborted,
        }
        self.ice_to_py_map = {i: p for p, i in self.py_to_ice_map.items()}

    @classmethod
    def _import_dto(cls):
        return dto.Status

    def _from_ice(self, dt: dto.Status) -> ExecutionStatus:
        return self.ice_to_py_map[dt]

    def _to_ice(self, bo: ExecutionStatus) -> dto.Status:
        return self.py_to_ice_map[bo]


@dc.dataclass
class SkillStatusUpdateHeader:
    skill_id: SkillID
    executor_name: str
    used_params: ty.Dict[str, ty.Any]
    used_callback_interface: callback_dti.SkillProviderCallbackInterfacePrx
    status: ExecutionStatus


class SkillStatusUpdateHeaderConv(IceConverter):

    def __init__(self):
        super().__init__()
        self.skill_id_conv = SkillIdConv()
        self.status_conv = ExecutionStatusConv()

    @classmethod
    def _import_dto(cls):
        return dto.SkillStatusUpdateHeader

    def _from_ice(self, dt: dto.SkillStatusUpdateHeader) -> SkillStatusUpdateHeader:
        return SkillStatusUpdateHeader(
            skill_id=self.skill_id_conv.from_ice(dt.skillId),
            executor_name=dt.executorName,
            used_params=aron_conv.pythonic_from_aron_ice(dt.usedParams),
            used_callback_interface=dt.usedCallbackInterface,
            status=self.status_conv.from_ice(dt.status),
        )

    def _to_ice(self, bo: SkillStatusUpdateHeader) -> dto.SkillStatusUpdate:
        return dto.SkillStatusUpdateHeader(
            skillId=self.skill_id_conv.to_ice(bo.skill_id),
            executorName=bo.executor_name,
            usedParams=aron_conv.pythonic_from_aron_ice(bo.used_params),
            usedCallbackInterface=bo.used_callback_interface,
            status=self.status_conv.to_ice(bo.status),
        )



@dc.dataclass
class SkillStatusUpdate:
    header: SkillStatusUpdateHeader
    data: ty.Dict[str, ty.Any]


class SkillStatusUpdateConv(IceConverter):

    def __init__(self):
        super().__init__()
        self.header_conv = SkillStatusUpdateHeaderConv()

    @classmethod
    def _import_dto(cls):
        return dto.SkillStatusUpdate

    def _from_ice(self, dt: dto.SkillStatusUpdate) -> SkillStatusUpdate:
        return SkillStatusUpdate(
            header=self.header_conv.from_ice(dt.header),
            data=aron_conv.pythonic_from_aron_ice(dt.data),
        )

    def _to_ice(self, bo: SkillStatusUpdate) -> dto.SkillStatusUpdate:
        return dto.SkillStatusUpdate(
            header=self.header_conv.to_ice(bo.header),
            data=aron_conv.pythonic_to_aron_ice(bo.data),
        )
