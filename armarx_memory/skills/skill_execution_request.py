import dataclasses as dc
import typing as ty

from armarx_memory.skills import dto
from armarx_memory.skills.skill_id import SkillID

from armarx_memory.ice_conv.ice_converter import IceConverter


@dc.dataclass
class SkillExecutionRequest:
    executor_name: str
    skill_id: SkillID
    params: ty.Dict[str, ty.Any]


class SkillExecutionRequestConv(IceConverter):

    @classmethod
    def _import_dto(cls):
        return dto.SkillExecutionRequest

    def _from_ice(self, dt: dto.SkillExecutionRequest) -> SkillExecutionRequest:
        return SkillExecutionRequest(provider_name=dt.providerName, skill_name=dt.skillName)

    def _to_ice(self, bo: SkillExecutionRequest) -> dto.SkillExecutionRequest:
        return dto.SkillExecutionRequest(providerName=bo.provider_name, skillName=bo.skill_name)
