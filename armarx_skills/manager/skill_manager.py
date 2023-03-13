import typing as ty

from armarx_core import ice_manager

from armarx_skills.manager import dti, dto
from armarx_skills.manager import skill_execution_request

from armarx_skills.provider import dto as provider_dto
from armarx_skills.provider import skill_status_update
from armarx_skills.provider.skill_id import SkillID



class SkillManager:

    DEFAULT_ICE_OBJECT_NAME = "SkillMemory"

    def __init__(
            self,
            proxy: dti.SkillManagerInterfacePrx = None,
    ):
        self.proxy = proxy

        self.skill_execution_request_conv = skill_execution_request.SkillExecutionRequestConv()
        self.skill_status_update_conv = skill_status_update.SkillStatusUpdateConv()

    @classmethod
    def wait_for_manager(cls, name=DEFAULT_ICE_OBJECT_NAME) -> "SkillManager":
        return cls(proxy=ice_manager.wait_for_proxy(dti.SkillManagerInterfacePrx, name))

    def add_provider(self, provider_info: dto.ProviderInfo) -> None:
        return self.proxy.addProvider(provider_info)

    def remove_provider(self, provider_info: dto.ProviderInfo) -> None:
        return self.proxy.removeProvider(providerInfo=provider_info)

    def get_skill_descriptions(self) -> dto.SkillDescriptionMapMap:
        return self.proxy.getSkillDescriptions()

    def get_skill_execution_statuses(self) -> dto.SkillStatusUpdateMapMap:
        return self.proxy.getSkillExecutionStatuses()

    def execute_skill(
            self,
            request: ty.Union[skill_execution_request.SkillExecutionRequest, dto.SkillExecutionRequest],
    ) -> skill_status_update.SkillStatusUpdate:
        request = self.skill_execution_request_conv.to_ice(request)
        update: provider_dto.SkillStatusUpdate = self.proxy.executeSkill(skillExecutionInfo=request)
        return self.skill_status_update_conv.from_ice(update)

    def execute_skill_with_default_params(
            self,
            executor_name: str,
            skill_id: SkillID,
    ):
        descriptions_ice = self.get_skill_descriptions()
        description_ice = descriptions_ice[skill_id.provider_name][skill_id.skill_name]
        default_params = description_ice.defaultParams

        self.execute_skill(skill_execution_request.SkillExecutionRequest(
            executor_name=executor_name,
            skill_id=skill_id,
            params=default_params,
        ))


    def abort_skill(self, provider_name: str, skill_name: str) -> None:
        return self.proxy.abortSkill(providerName=provider_name, skillName=skill_name)


class ReconnectingSkillManager:

    def __init__(self):
        self._skill_manager: ty.Optional[SkillManager] = None

    def get(self, logger=None) -> SkillManager:
        self.connect(logger=logger)
        return self._skill_manager

    def connect(self, logger=None):
        if self._skill_manager is None:
            name = SkillManager.DEFAULT_ICE_OBJECT_NAME
            if logger is not None:
                logger.info(f"Waiting for skill manager '{name}' ...")
            self._skill_manager = SkillManager.wait_for_manager(name=name)


if __name__ == '__main__':
    def test_main():
        manager = SkillManager.wait_for_manager()
        manager.get_skill_execution_statuses()

    test_main()
