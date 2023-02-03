import dataclasses as dc

from armarx_memory.skills.provider import dto

from armarx_memory.ice_conv.ice_converter import IceConverter


@dc.dataclass
class SkillID:
    provider_name: str
    skill_name: str


class SkillIdConv(IceConverter):

    @classmethod
    def _import_dto(cls):
        return dto.SkillID

    def _from_ice(self, dt: dto.SkillID) -> SkillID:
        return SkillID(provider_name=dt.providerName, skill_name=dt.skillName)

    def _to_ice(self, bo: SkillID) -> dto.SkillID:
        return dto.SkillID(providerName=bo.provider_name, skillName=bo.skill_name)
