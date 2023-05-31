from armarx_core.error import ArmarXCoreError


class ArmarXSkillsError(ArmarXCoreError):
    """
    Base class of Exceptions raised by the armarx_skills subpackage.
    """
    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)


class SkillProviderUnknown(ArmarXSkillsError):
    def __init__(
            self,
            skill_provider_name: str,
            *args,
            **kwargs,
    ):
        self.skill_provider_name = skill_provider_name
        super().__init__(f"Skill provider '{skill_provider_name}' unknown.", *args, **kwargs)

    def __str__(self):
        return f"Could not find skill provider '{self.skill_provider_name}'."


class SkillUnknown(ArmarXSkillsError):

    def __init__(
            self,
            skill_name: str,
            *args,
            **kwargs,
    ):
        self.skill_name = skill_name
        super().__init__(f"Skill '{skill_name}' unknown.", *args, **kwargs)

    def __str__(self):
        return f"Could not find skill '{self.skill_name}'."

