import typing as ty

from armarx_core import ice_manager

from armarx_memory.skills import dti, dto


class SkillManager:

    DEFAULT_ICE_OBJECT_NAME = "SkillMemory"

    def __init__(
            self,
            proxy: dti.SkillManagerInterfacePrx = None,
    ):
        self.proxy = proxy

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

    def execute_skill(self, skill_execution_info: dto.SkillExecutionRequest) -> dto.SkillStatusUpdate:
        return self.proxy.executeSkill(skillExecutionInfo=skill_execution_info)

    def abort_skill(self, provider_name: str, skill_name: str) -> None:
        return self.proxy.abortSkill(providerName=provider_name, skillName=skill_name)


if __name__ == '__main__':
    manager = SkillManager.wait_for_manager()
    manager.get_skill_execution_statuses()
