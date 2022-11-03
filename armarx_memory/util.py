from typing import Optional

from armarx_core import slice_loader

slice_loader.load_armarx_slice("RobotAPI", "aron.ice")
slice_loader.load_armarx_slice("RobotAPI", "armem/memory.ice")

from armarx import aron
from armarx import armem


def get_latest_data(
    entity: armem.data.Entity,
    instance_index=0,
) -> "aron.AronData":
    snapshot: armem.data.EntitySnapshot = list(entity.history.values())[-1]
    instance: armem.data.EntityInstance = snapshot.instances[instance_index]
    return instance.data


def find_entity_by_name(
    name: str,
    core_segment: armem.data.CoreSegment,
) -> Optional[armem.data.Entity]:
    # Find class
    for prov_name, prov in core_segment.providerSegments.items():
        for entity_name, entity in prov.entities.items():
            if entity_name == name:
                return entity
    return None
