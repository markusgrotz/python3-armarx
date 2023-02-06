#!/usr/bin/env python3

from armarx_skills.provider.skill_id import SkillID
from armarx_skills.manager.skill_manager import SkillManager
from armarx_skills.manager.skill_execution_request import SkillExecutionRequest


def main():
    name = "execute_skill_example"

    manager = SkillManager.wait_for_manager()

    statuses = manager.get_skill_execution_statuses()
    for x_name, update_map in statuses.items():
        print(f"- '{x_name}'")
        for y_name, update in update_map.items():
            print(f"  - '{y_name}':")
            print(update)

    execution_req = SkillExecutionRequest(
        executor_name=name,
        skill_id=SkillID(
            provider_name="SkillProviderExample",
            skill_name="HelloWorld",
        ),
        params={
            "some_float": 42.0,
            "some_int": 0x42,
            "some_text": "fourty two",
        }
    )
    manager.execute_skill()


if __name__ == "__main__":
    main()
