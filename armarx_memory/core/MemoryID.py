import copy
import enum

import armarx
from armarx_core import slice_loader

slice_loader.load_armarx_slice("RobotAPI", "armem/memory.ice")
from armarx import armem

from armarx_memory.ice_conv import ice_twin
from armarx_memory.core.time import DateTimeIceConverter

date_time_conv = DateTimeIceConverter()


class MemoryID(ice_twin.IceTwin):
    def __init__(
        self,
        memory_name: str = "",
        core_segment_name: str = "",
        provider_segment_name: str = "",
        entity_name: str = "",
        timestamp_usec: int = -1,
        instance_index: int = -1,
    ):
        self.memory_name = memory_name
        self.core_segment_name = core_segment_name
        self.provider_segment_name = provider_segment_name
        self.entity_name = entity_name
        self.timestamp_usec = timestamp_usec
        self.instance_index = instance_index

    @classmethod
    def from_string(cls, string: str):
        items = string.split("/")
        # Handle escaped /'s
        i = 0
        while i < len(items):
            item = items[i]
            while len(item) > 0 and item[-1] == "\\":
                # The / causing the split was escaped. Merge the items together.
                if i < len(items):
                    items[i] = item[:-1] + "/" + items[i + 1]
                    del items[i]
            i += 1

        self = cls()
        try:
            # Set as much as possible until an index error occurs.
            self.memory_name = items[0]
            self.core_segment_name = items[1]
            self.provider_segment_name = items[2]
            self.entity_name = items[3]
            self.timestamp_usec = int(items[4])
            self.instance_index = int(items[5])
        except IndexError:
            pass

        return self

    def set_memory_id(self, id: "MemoryID"):
        self.memory_name = id.memory_name

    def set_core_segment_id(self, id: "MemoryID"):
        self.set_memory_id(id)
        self.core_segment_name = id.core_segment_name

    def set_provider_segment_id(self, id: "MemoryID"):
        self.set_core_segment_id(id)
        self.provider_segment_name = id.provider_segment_name

    def set_entity_id(self, id: "MemoryID"):
        self.set_provider_segment_id(id)
        self.entity_name = id.entity_name

    def set_snapshot_id(self, id: "MemoryID"):
        self.set_entity_id(id)
        self.timestamp_usec = id.timestamp_usec

    def set_instance_id(self, id: "MemoryID"):
        self.set_snapshot_id(id)
        self.instance_index = id.instance_index

    def with_memory_name(self, name: str) -> "MemoryID":
        c = copy.copy(self)
        c.memory_name = name
        return c

    def with_core_segment_name(self, name: str) -> "MemoryID":
        c = copy.copy(self)
        c.core_segment_name = name
        return c

    def with_provider_segment_name(self, name: str) -> "MemoryID":
        c = copy.copy(self)
        c.provider_segment_name = name
        return c

    def with_entity_name(self, name: str) -> "MemoryID":
        c = copy.copy(self)
        c.entity_name = name
        return c

    def with_timestamp(self, time_usec: int) -> "MemoryID":
        c = copy.copy(self)
        c.timestamp_usec = time_usec
        return c

    def with_instance_index(self, index: int) -> "MemoryID":
        c = copy.copy(self)
        c.instance_index = index
        return c

    def contains(self, id: "MemoryID"):
        general = self
        specific = id
        if general.memory_name == "":
            return True
        elif general.memory_name != specific.memory_name:
            return False

        if general.core_segment_name == "":
            return True
        elif general.core_segment_name != specific.core_segment_name:
            return False

        if general.provider_segment_name == "":
            return True
        elif general.provider_segment_name != specific.provider_segment_name:
            return False

        if general.entity_name == "":
            return True
        elif general.entity_name != specific.entity_name:
            return False

        if general.timestamp_usec is None or general.timestamp_usec < 0:
            return True
        elif general.timestamp_usec != specific.timestamp_usec:
            return False

        if general.instance_index < 0:
            return True
        elif general.instance_index != specific.instance_index:
            return False

    def __eq__(self, other):
        if other is None or not isinstance(other, MemoryID):
            return False

        return (
            other.memory_name == self.memory_name
            and other.core_segment_name == self.core_segment_name
            and other.provider_segment_name == self.provider_segment_name
            and other.entity_name == self.entity_name
            and other.instance_index == self.instance_index
            and other.timestamp_usec == self.timestamp_usec
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # Just use two values to make has computation more efficient.
        return hash((self.timestamp_usec, self.instance_index, self.entity_name))

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.__str__())

    def __str__(self):
        return "'{}'".format("/".join(map(str, self.get_set_items())))

    def get_set_items(self):
        items = [self.memory_name]

        if not self.core_segment_name:
            return items
        items.append(self.core_segment_name)

        if not self.provider_segment_name:
            return items
        items.append(self.provider_segment_name)

        if not self.entity_name:
            return items
        items.append(self.entity_name)

        if self.timestamp_usec < 0:
            return items
        items.append(self.timestamp_usec)

        if self.instance_index < 0:
            return items
        items.append(self.instance_index)

        return items

    def get_all_items(self):
        return [
            self.memory_name,
            self.core_segment_name,
            self.provider_segment_name,
            self.entity_name,
            self.timestamp_usec,
            self.instance_index,
        ]

    def _get_ice_cls(self):
        return armem.data.MemoryID

    def _set_to_ice(self, ice: "armem.data.Commit"):
        ice.memoryName = self.memory_name
        ice.coreSegmentName = self.core_segment_name
        ice.providerSegmentName = self.provider_segment_name
        ice.entityName = self.entity_name
        ice.timestamp = date_time_conv.to_ice(self.timestamp_usec)
        ice.instanceIndex = self.instance_index

    def _set_from_ice(self, ice):
        self.memory_name = ice.memoryName
        self.core_segment_name = ice.coreSegmentName
        self.provider_segment_name = ice.providerSegmentName
        self.entity_name = ice.entityName
        self.timestamp_usec = date_time_conv.from_ice(ice.timestamp)
        self.instance_index = ice.instanceIndex

    @classmethod
    def from_aron(cls, aron: "armarx.aron.data.dto.GenericData") -> "MemoryID":
        from armarx_memory.aron.conversion import from_aron

        data = from_aron(aron)
        self = cls()
        self.memory_name = data["memoryName"]
        self.core_segment_name = data["coreSegmentName"]
        self.provider_segment_name = data["providerSegmentName"]
        self.entity_name = data["entityName"]
        self.timestamp_usec = int(data["timestamp"])
        self.instance_index = data["instanceIndex"]
        return self

    def to_aron(self) -> "armarx.aron.data.dto.GenericData":
        import numpy as np
        from armarx_memory.aron.conversion import to_aron

        class ClockType(enum.IntEnum):
            REALTIME = 0  # Normalized time as reported by the operating system.
            MONOTONIC = 1  # Monotonic/steady clock of the operating system.
            VIRTUAL = 2  # Time given by time-server if configured, realtime otherwise.
            UNKNOWN = 3  # Unknown source of time.

        data = {
            "memoryName": self.memory_name,
            "coreSegmentName": self.core_segment_name,
            "providerSegmentName": self.provider_segment_name,
            "entityName": self.entity_name,
            "timestamp": {
                "clockType": ClockType.VIRTUAL,
                "hostname": "unknown",
                "timeSinceEpoch": {
                    "microSeconds": np.int64(self.timestamp_usec),
                },
            },
            "instanceIndex": self.instance_index,
        }
        return to_aron(data)
