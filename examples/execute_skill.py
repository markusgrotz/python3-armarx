
import armarx
from armarx_skills.provider.skill_id import SkillID
from armarx_skills.manager.skill_manager import SkillManager
from armarx_skills.manager.skill_execution_request import SkillExecutionRequest


if __name__ == '__main__':

    name = "execute_skill.py"

    skill_manager = SkillManager.wait_for_manager()

    # skill_id = SkillID("introduction_skill_provider", "IntroduceYourself")
    # skill_id = SkillID("introduction_skill_provider", "IntroduceYourselfAtLocation")

    # skill_manager.execute_skill_with_default_params(executor_name=name, skill_id=skill_id)

    skill_id = SkillID("bring_object_from_kitchen_to_human", "BringObjectFromKitchenToHuman")
    skill_manager.execute_skill(SkillExecutionRequest(
        executor_name=name,
        skill_id=skill_id,
        params={
            "objectPhrase": "apple tea",
            "utterance": "bring me the apple tea from the kitchen",
        }
    ))
