from typing import List, Optional
import time

from armarx_memory.aron.conversion import Aron
from armarx_memory.core import MemoryID, time_usec
from armarx_memory.ice_conv import ice_twin


from armarx import slice_loader
slice_loader.load_armarx_slice("RobotAPI", "armem/server/MemoryInterface.ice")

import armarx.armem as armem


class EntityUpdate(ice_twin.IceTwin):

    def __init__(
            self,
            entity_id: MemoryID = None,
            instances_data: List[Aron.Data] = None,
            time_created_usec: Optional[int] = None,
            confidence: Optional[float] = None,
            time_sent_usec: Optional[int] = None,
            ):

        self.entity_id: MemoryID = entity_id or MemoryID()
        self.instances_data = instances_data or []

        self.time_created_usec = time_created_usec or time_usec()

        self.confidence = 1.0 if confidence is None else float(confidence)
        self.time_sent_usec: Optional[int] = time_sent_usec


    def set_time_created_to_now(self):
        self.time_created_usec = self.now()


    @staticmethod
    def now():
        return time_usec()


    @classmethod
    def _get_ice_cls(cls):
        return armem.data.EntityUpdate


    def _set_to_ice(self, dto: armem.data.EntityUpdate):
        assert self.time_created_usec > 0, f"The time sent must be valid: {self.time_created_usec}"
        assert self.time_sent_usec > 0 or self.time_sent_usec is None, f"The time sent must be valid: {self.time_created_usec}"

        dto.entityID = self.entity_id.to_ice()
        dto.instancesData = self.instances_data
        dto.timeCreated.timeSinceEpoch.microSeconds = self.time_created_usec

        dto.confidence = self.confidence
        dto.timeSent.timeSinceEpoch.microSeconds = self.time_sent_usec if self.time_sent_usec is not None else time.time()


    def _set_from_ice(self, dto):
        self.entity_id.set_from_ice(dto.entityID)
        self.instances_data = dto.instancesData
        self.time_created_usec = dto.timeCreated.timeSinceEpoch.microSeconds

        self.confidence = dto.confidence
        self.time_sent_usec = dto.timeSent.timeSinceEpoch.microSeconds

        assert self.time_created_usec > 0, f"The time sent must be valid: {self.time_created_usec}"
        assert self.time_sent_usec > 0 or self.time_sent_usec is None, f"The time sent must be valid: {self.time_created_usec}"


    def __repr__(self):
        return "<{c} id={i} t={t} c={con:.3f} with {n} instance{ns}>".format(
            c=self.__class__.__name__,
            i=self.entity_id,
            t=self.time_created_usec,
            n=len(self.instances_data),
            ns="" if len(self.instances_data) == 1 else "s",
            con=self.confidence,
            # d=self.instances_data,
        )


class Commit(ice_twin.IceTwin):

    def __init__(self, updates: List[EntityUpdate] = None):
        self.updates = updates or []


    def add(self, update: Optional[EntityUpdate] = None,
            **kwargs):
        if update is None:
            update = EntityUpdate(**kwargs)
        self.updates.append(update)
        return update


    @classmethod
    def _get_ice_cls(cls):
        return armem.data.Commit


    def _set_to_ice(self, dto: armem.data.Commit):
        dto.updates = ice_twin.to_ice(self.updates)


    def _set_from_ice(self, dto):
        self.updates = EntityUpdate.from_ice(dto.updates)

    def __repr__(self):
        return "<{c} with {n} update{ns}>".format(
            c=self.__class__.__name__,
            n=len(self.updates),
            ns="" if len(self.updates) == 1 else "s",
        )

    def __str__(self):
        return "{r}\n- {u}".format(
            r=self.__repr__(),
            u="n- ".join(map(str, self.updates))
        )
