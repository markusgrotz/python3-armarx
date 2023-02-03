import typing as ty

from armarx_memory.skills.slice import load_slice

load_slice()


from armarx.skills.provider.dto import \
    SkillID, SkillDescription, SkillExecutionRequest, SkillStatusUpdateHeader, SkillStatusUpdate
from armarx.skills.provider.dto.Execution import Status


SkillDescriptionMap = ty.Dict[str, SkillDescription]
SkillStatusUpdateMap = ty.Dict[str, SkillStatusUpdate]

