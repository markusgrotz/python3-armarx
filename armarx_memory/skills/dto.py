import typing as ty

from armarx_memory.skills.slice import load_slice

load_slice()


# Provider

from armarx.skills.provider.dto import \
    SkillID, SkillDescription, SkillExecutionRequest, SkillStatusUpdateHeader, SkillStatusUpdate
from armarx.skills.provider.dto.Execution import Status

# Manager

from armarx.skills.manager.dto import SkillExecutionRequest
from armarx.skills.manager.dto import ProviderInfo


# Provider

SkillDescriptionMap = ty.Dict[str, SkillDescription]
SkillStatusUpdateMap = ty.Dict[str, SkillStatusUpdate]


# Manager

SkillDescriptionMapMap = ty.Dict[str, SkillDescriptionMap]
SkillStatusUpdateMapMap = ty.Dict[str, SkillDescriptionMapMap]
