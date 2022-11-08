from armarx_robots.armar_6 import A6
from armarx_robots.armar_de import AD
from armarx_robots.armar_3 import A3


def robot_by_name(robot_name: str = None):
    if robot_name == "A6":
        return A6()
    elif robot_name == "AD":
        return AD()
    elif robot_name == "A3":
        return A3()
    return None
