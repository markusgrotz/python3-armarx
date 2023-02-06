#!/usr/bin/env python3

import armarx
from armarx_skills.provider.skill_id import SkillID
from armarx_skills.manager.skill_manager import SkillManager
from armarx_skills.manager.skill_execution_request import SkillExecutionRequest


def main():
    """
    To run the example:
    1. Start ArmarX
    2. Start the scenario ArMemCore (RobotAPI)
    3. Start the component SkillsMemory (RobotAPI)
    4. Start the component SkillProviderExample (RobotAPI)
    5. Run this script.
    """

    name = "execute_skill_example"

    manager = SkillManager.wait_for_manager()

    # Get skill execution statuses.
    statuses = manager.get_skill_execution_statuses()
    for provider_name, update_map in statuses.items():
        print(f"- Provider '{provider_name}'")
        for skill_name, update in update_map.items():
            print(f"  - Skill '{skill_name}': {update}")

    # Execute a skill.
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
    print(f"Request: {execution_req}")
    status_update = manager.execute_skill(request=execution_req)
    print(f"Status update: {status_update}")


if __name__ == "__main__":
    main()
