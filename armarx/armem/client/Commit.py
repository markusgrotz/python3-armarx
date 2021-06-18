import time
from typing import Dict, Any, List, Optional, Callable, Union

from armarx.ice_conv import IceTwin
from armarx.armem.core import MemoryID

from armarx import slice_loader
slice_loader.load_armarx_slice("RobotAPI", "armem/server/MemoryInterface.ice")

import armarx.aron as aron
import armarx.armem as armem


class EntityUpdate(IceTwin):

    def __init__(
            self,
            entity_id: MemoryID = None,
            instances_data: List[aron.data.AronData] = None,
            time_created_usec: Optional[int] = None,
            confidence: float = 1.0,
            time_sent_usec: Optional[int] = None,
            ):

        self.entity_id: MemoryID = entity_id or MemoryID()
        self.instances_data = instances_data or []

        self.time_created_usec = time_created_usec or time_usec()

        self.confidence = confidence
        self.time_sent_usec: Optional[int] = time_sent_usec


    def set_time_created_to_now(self):
        self.time_created_usec = time_usec()


    @classmethod
    def _get_ice_cls(cls):
        return armem.data.EntityUpdate


    def _set_to_ice(self, dto: armem.data.Commit):
        dto.entityID = self.entity_id.to_ice()
        dto.instancesData = self.instances_data
        dto.timeCreatedMicroSeconds = self.time_created_usec

        dto.confidence = self.confidence
        dto.timeSentMicroSeconds = self.time_sent_usec if self.time_sent_usec is not None else -1


    def _set_from_ice(self, dto):
        self.entity_id.set_from_ice(dto.entityID)
        self.instances_data = dto.instancesData
        self.time_created_usec = dto.timeCreatedMicroSeconds

        self.confidence = dto.confidence
        self.time_sent_usec = dto.timeSentMicroSeconds



class Commit(IceTwin):

    def __init__(self, updates: List[EntityUpdate] = None):
        self.updates = updates or []


    def add(self, update: Optional[EntityUpdate] = None):
        if update is None:
            update = EntityUpdate()
        self.updates.append(update)
        return update


    @classmethod
    def _get_ice_cls(cls):
        return armem.data.Commit


    def _set_to_ice(self, dto: armem.data.Commit):
        dto.updates = icetwin.to_ice(self.updates)


    def _set_from_ice(self, dto):
        self.updates = EntityUpdate.from_ice(dto.updates)
