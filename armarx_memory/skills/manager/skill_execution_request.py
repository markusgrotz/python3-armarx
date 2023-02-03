import dataclasses as dc
import typing as ty

from armarx_memory.skills.manager import dto

from armarx_memory.ice_conv.ice_converter import IceConverter
from armarx_memory.aron.conversion import pythonic_from_to_aron_ice

from armarx_memory.skills.provider.skill_id import SkillID, SkillIdConv


@dc.dataclass
class SkillExecutionRequest:
    executor_name: str
    skill_id: SkillID
    params: ty.Dict[str, ty.Any]


class SkillExecutionRequestConv(IceConverter):

    def __init__(self):
        super().__init__()
        self.skill_id_conv = SkillIdConv()

    @classmethod
    def _import_dto(cls):
        return dto.SkillExecutionRequest

    def _from_ice(self, dt: dto.SkillExecutionRequest) -> SkillExecutionRequest:
        return SkillExecutionRequest(
            executor_name=dt.executorName,
            skill_id=self.skill_id_conv.from_ice(dt.skillId),
            params=pythonic_from_to_aron_ice.pythonic_from_aron_ice(dt.params),
        )

    def _to_ice(self, bo: SkillExecutionRequest) -> dto.SkillExecutionRequest:
        return dto.SkillExecutionRequest(
            executorName=bo.executor_name,
            skillId=self.skill_id_conv.to_ice(bo.skill_id),
            params=pythonic_from_to_aron_ice.pythonic_to_aron_ice(bo.params),
        )
