import typing as ty

from armarx_memory.skills.slice import load_slice

from armarx_memory.skills.provider.dto import SkillDescriptionMap
from armarx_memory.skills.provider.dto import SkillStatusUpdateMap

load_slice()

from armarx.skills.manager.dto import SkillExecutionRequest
from armarx.skills.manager.dto import ProviderInfo

SkillDescriptionMapMap = ty.Dict[str, SkillDescriptionMap]
SkillStatusUpdateMapMap = ty.Dict[str, SkillStatusUpdateMap]
