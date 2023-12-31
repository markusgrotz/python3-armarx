from typing import List, Optional

from armarx_memory.aron.aron_ice_types import AronIceTypes
from armarx_memory.core import MemoryID, time_usec, DateTimeIceConverter
from armarx_memory.ice_conv import ice_twin


from armarx_core import slice_loader

slice_loader.load_armarx_slice("RobotAPI", "armem/server/MemoryInterface.ice")

import armarx.armem as armem

date_time_conv = DateTimeIceConverter()


class EntityUpdate(ice_twin.IceTwin):
    def __init__(
        self,
        entity_id: MemoryID = None,
        instances_data: List[AronIceTypes.Data] = None,
        referenced_time_usec: Optional[int] = None,
        confidence: Optional[float] = None,
        time_sent_usec: Optional[int] = None,
    ):

        self.entity_id: MemoryID = entity_id or MemoryID()
        self.instances_data = instances_data or []

        self.referenced_time_usec = referenced_time_usec or time_usec()

        self.confidence = 1.0 if confidence is None else float(confidence)
        self.time_sent_usec: Optional[int] = time_sent_usec

    def set_referenced_time_to_now(self):
        self.referenced_time_usec = self.now()

    @staticmethod
    def now():
        return time_usec()

    @classmethod
    def _get_ice_cls(cls):
        return armem.data.EntityUpdate

    def _set_to_ice(self, dto: armem.data.Commit):
        dto.entityID = self.entity_id.to_ice()
        dto.instancesData = self.instances_data
        dto.referencedTime = date_time_conv.to_ice(self.referenced_time_usec)

        dto.confidence = self.confidence
        dto.sentTime = date_time_conv.to_ice(
            self.time_sent_usec if self.time_sent_usec is not None else -1
        )

    def _set_from_ice(self, dto):
        self.entity_id.set_from_ice(dto.entityID)
        self.instances_data = dto.instancesData
        self.referenced_time_usec = date_time_conv.from_ice(dto.referencedTime)

        self.confidence = dto.confidence
        self.time_sent_usec = date_time_conv.from_ice(dto.sentTime)

        assert (
            self.referenced_time_usec > 0
        ), f"The time sent must be valid: {self.referenced_time_usec}"
        assert (
            self.time_sent_usec > 0 or self.time_sent_usec is None
        ), f"The time sent must be valid: {self.time_sent_usec}"

    def __repr__(self):
        return "<{c} id={i} t={t} c={con:.3f} with {n} instance{ns}>".format(
            c=self.__class__.__name__,
            i=self.entity_id,
            t=self.referenced_time_usec,
            n=len(self.instances_data),
            ns="" if len(self.instances_data) == 1 else "s",
            con=self.confidence,
            # d=self.instances_data,
        )


class Commit(ice_twin.IceTwin):
    def __init__(self, updates: List[EntityUpdate] = None):
        self.updates = updates or []

    def add(self, update: Optional[EntityUpdate] = None, **kwargs):
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
            r=self.__repr__(), u="n- ".join(map(str, self.updates))
        )
