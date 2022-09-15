from abc import ABC
from abc import abstractmethod

from typing import List
from typing import Optional


from armarx_memory.core import MemoryID
from armarx_memory.client import MemoryNameSystem
from armarx_memory.client import Commit
from armarx_memory.client import Reader
from armarx_memory.client import Writer


class GenericDataClass:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_aron(self) -> "armarx.aron.data.dto.GenericData":
        from armarx_memory.aron.conversion import to_aron

        return to_aron(self.__dict__)

    @classmethod
    def from_aron(cls, dto: "armarx.aron.data.dto.GenericData"):
        from armarx_memory.aron.conversion import from_aron

        return cls(**from_aron(dto))


class BaseClient(ABC):
    @property
    @abstractmethod
    def core_segment_id(self):
        pass

    @property
    @abstractmethod
    def default_entity_name(self):
        pass

    def make_entity_name(self, provider_name: str, entity_name: str = None):
        if not entity_name:
            entity_name = self.default_entity_name
        return self.core_segment_id.with_provider_segment_name(
            provider_name
        ).with_entity_name(entity_name)


class BaseReader(Reader, BaseClient, ABC):
    def fetch_latest_instance(self, updated_ids: Optional[List[MemoryID]] = None):
        """
        Query the latest snapshot of the given updated IDs and
        return its first instance.
        """
        if updated_ids is None:
            memory = self.query_latest(self.core_segment_id)

            latest_snapshot = None

            core_seg = memory.coreSegments[self.core_segment_id.core_segment_name]
            for prov_seg in core_seg.providerSegments.values():
                for entity in prov_seg.entities.values():
                    for snapshot in entity.history.values():
                        if latest_snapshot is None:
                            latest_snapshot = snapshot
                        elif (
                            latest_snapshot.id.timestamp.timeSinceEpoch.microSeconds
                            < snapshot.id.timestamp.timeSinceEpoch.microSeconds
                        ):
                            latest_snapshot = snapshot
        else:
            for up_id in updated_ids:
                assert self.core_segment_id.contains(up_id)

            latest_snapshot_id = max(updated_ids, key=lambda i: i.timestamp_usec)
            latest_snapshot = self.query_snapshot(latest_snapshot_id)

        if not latest_snapshot:
            return None

        latest_instance = latest_snapshot.instances[0]
        return latest_instance

    @classmethod
    def from_mns(cls, mns: MemoryNameSystem = None, wait=True):
        if not mns:
            mns = MemoryNameSystem.get_mns()
        if wait:
            return cls(mns.wait_for_server(cls.core_segment_id).reading)
        else:
            return cls(mns.resolve_server(cls.core_segment_id).reading)


class BaseWriter(BaseClient, ABC):
    def __init__(self, writer: Writer):
        super().__init__()
        self.writer = writer

    def commit(self, entity_id: MemoryID, time_created_usec=None, **kwargs):
        from armarx_memory.aron.conversion import to_aron

        commit = Commit()
        commit.add(
            entity_id=entity_id,
            time_created_usec=time_created_usec,
            instances_data=[to_aron(kwargs)],
        )
        return self.writer.commit(commit.to_ice())

    @classmethod
    def from_mns(cls, mns: MemoryNameSystem = None, wait=True):
        if not mns:
            mns = MemoryNameSystem.get_mns()
        if wait:
            return cls(mns.wait_for_server(cls.core_segment_id).writing)
        else:
            return cls(mns.resolve_server(cls.core_segment_id).writing)
