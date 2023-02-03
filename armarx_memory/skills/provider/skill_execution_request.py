import dataclasses as dc
import typing as ty

from armarx_memory.skills.callback import dti as callback_dti
from armarx_memory.skills.provider import dti as provider_dto
from armarx_memory.skills.provider import dto as provider_dto

from armarx_memory.ice_conv.ice_converter import IceConverter
from armarx_memory.aron.conversion import pythonic_from_to_aron_ice


@dc.dataclass
class SkillExecutionRequest:
    skill_name: str
    executor_name: str
    params: ty.Dict[str, ty.Any]
    callback_interface: ty.Optional[callback_dti.SkillProviderCallbackInterfacePrx] = None


class SkillExecutionRequestConv(IceConverter):

    @classmethod
    def _import_dto(cls):
        return provider_dto.SkillExecutionRequest

    def _from_ice(self, dt: provider_dto.SkillExecutionRequest) -> SkillExecutionRequest:
        return SkillExecutionRequest(
            skill_name=dt.skillName,
            executor_name=dt.executorName,
            params=pythonic_from_to_aron_ice.pythonic_from_aron_ice(dt.params),
            callback_interface=dt.callbackInterface,
        )

    def _to_ice(self, bo: SkillExecutionRequest) -> provider_dto.SkillExecutionRequest:
        return provider_dto.SkillExecutionRequest(
            skillName=bo.skill_name,
            executorName=bo.executor_name,
            params=pythonic_from_to_aron_ice.pythonic_to_aron_ice(bo.params),
            callbackInterface=bo.callback_interface,
        )
