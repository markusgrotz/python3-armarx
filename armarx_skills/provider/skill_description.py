import dataclasses as dc
import typing as ty

from armarx_core.time import date_time
from armarx_memory.aron import aron_dataclass
from armarx_memory.ice_conv.ice_converter import IceConverter
from armarx_skills.provider import dto

import armarx.aron.type.dto


@dc.dataclass
class SkillDescription:
    skill_name: str = "UNINITIALIZED SKILL NAME"
    description: str = "UNINITIALIZED SKILL DESCRIPTION"
    robots: ty.List[str] = dc.field(default_factory=list)
    timeout_usec: int = date_time.INVALID_TIME_USEC
    # ::armarx::aron::type::dto::AronObjectPtr / armarx::aron::type::ObjectPtr
    # accepted_type: ty.Optional[aron_dataclass.AronDataclass.__class__] = None
    accepted_type: ty.Optional[armarx.aron.type.dto.AronObject] = None
    # ::armarx::aron::data::dto::DictPtr / armarx::aron::data::DictPtr
    default_params: ty.Optional[aron_dataclass.AronDict] = None


class SkillDescriptionConv(IceConverter):

    @classmethod
    def _import_dto(cls):
        return dto.SkillDescription

    def _from_ice(self, dt: dto.SkillDescription) -> SkillDescription:
        return SkillDescription(
            skill_name=dt.skillName,
            description=dt.description,
            robots=dt.robots,
            timeout_usec=dt.timeoutMs * 1_000,
            accepted_type=dt.acceptedType,
            default_params=dt.defaultParams,
        )

    def _to_ice(self, bo: SkillDescription) -> dto.SkillDescription:
        return dto.SkillDescription(
            skillName=bo.skill_name,
            description=bo.description,
            robots=bo.robots,
            timeoutMs=int(bo.timeout_usec / 1_000),
            acceptedType=bo.accepted_type,
            defaultParams=bo.default_params,
        )
