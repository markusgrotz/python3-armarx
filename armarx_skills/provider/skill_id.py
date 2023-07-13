import dataclasses as dc

from armarx_skills.provider import dto

from armarx_memory.ice_conv.ice_converter import IceConverter

PREFIX_SEPARATOR = "->"
NAME_SEPARATOR = "/"


@dc.dataclass
class SkillID:
    provider_name: str
    skill_name: str

    def to_str(self, prefix: str):
        # # return (prefix.empty() ? std::string("") : (prefix + PREFIX_SEPARATOR)) + providerName + NAME_SEPARATOR + skillName;
        return "".join([("" if len(prefix) == 0 else (prefix + PREFIX_SEPARATOR)),
                        self.provider_name, NAME_SEPARATOR, self.skill_name])

    def __str__(self):
        # return (prefix.empty() ? std::string("") : (prefix + PREFIX_SEPARATOR)) + providerName + NAME_SEPARATOR + skillName;

        return f"{self.skill_name}"


class SkillIdConv(IceConverter):

    @classmethod
    def _import_dto(cls):
        return dto.SkillID

    def _from_ice(self, dt: dto.SkillID) -> SkillID:
        return SkillID(provider_name=dt.providerName, skill_name=dt.skillName)

    def _to_ice(self, bo: SkillID) -> dto.SkillID:
        return dto.SkillID(providerName=bo.provider_name, skillName=bo.skill_name)
