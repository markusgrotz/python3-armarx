import armarx
from armarx import slice_loader

slice_loader.load_armarx_slice("RobotAPI", "armem/memory.ice")
slice_loader.load_armarx_slice("RobotAPI", "armem/commit.ice")
from armarx import armem

from armarx.ice_conv import IceTwin


class MemoryID(icetwin.IceTwin):

    def __init__(self,
                 memory_name: str = "",
                 core_segment_name: str = "",
                 provider_segment_name: str = "",
                 entity_name: str = "",
                 timestamp_usec: int = -1,
                 instance_index: int = -1):
        self.memory_name = memory_name
        self.core_segment_name = core_segment_name
        self.provider_segment_name = provider_segment_name
        self.entity_name = entity_name
        self.timestamp_usec = timestamp_usec
        self.instance_index = instance_index

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

        return (other.memory_name == self.memory_name
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
        return [self.memory_name, self.core_segment_name,
                self.provider_segment_name, self.entity_name,
                self.timestamp_usec, self.instance_index]

    def get_ice_cls(self):
        return armem.data.MemoryID

    def set_to_ice(self, ice: armem.data.Commit):
        ice.memoryName = self.memory_name
        ice.coreSegmentName = self.core_segment_name
        ice.providerSegmentName = self.provider_segment_name
        ice.entityName = self.entity_name
        ice.timestampMicroSeconds = self.timestamp_usec
        ice.instanceIndex = self.instance_index

    def set_from_ice(self, ice):
        self.memory_name = ice.memoryName
        self.core_segment_name = ice.coreSegmentName
        self.provider_segment_name = ice.providerSegmentName
        self.entity_name = ice.entityName
        self.timestamp_usec = ice.timestampMicroSeconds
        self.instance_index = ice.instanceIndex

    @classmethod
    def from_aron(cls, aron: "armarx.aron.data.AronData") -> "MemoryID":
        import verbalmanipulation.memory.aron_conv as aron_conv
        data = aron_conv.from_aron(aron)
        self = cls()
        self.memory_name = data["memoryName"]
        self.core_segment_name = data["coreSegmentName"]
        self.provider_segment_name = data["providerSegmentName"]
        self.entity_name = data["entityName"]
        self.timestamp_usec = int(data["timestamp"])
        self.instance_index = data["instanceIndex"]
        return self


    def to_aron(self) -> "armarx.aron.data.AronData":
        import verbalmanipulation.memory.aron_conv as aron_conv
        import numpy as np

        data = {
            "memoryName": self.memory_name,
            "coreSegmentName": self.core_segment_name,
            "providerSegmentName": self.provider_segment_name,
            "entityName": self.entity_name,
            "timestamp": np.int64(self.timestamp_usec),
            "instanceIndex": self.instance_index
        }
        return aron_conv.to_aron(data)
