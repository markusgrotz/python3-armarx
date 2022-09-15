from typing import List, Optional

import numpy as np

from armarx_memory.client import MemoryNameSystem, Commit, Reader, Writer
from armarx_memory.core import MemoryID


class PersonInstance:
    def __init__(self, personID: MemoryID, pose: np.ndarray):
        self.personID = personID
        self.pose = pose

    def to_aron(self) -> "armarx.aron.data.dto.GenericData":
        from armarx_memory.aron.conversion import to_aron

        dto = to_aron({"personID": self.personID, "pose": self.pose})
        return dto

    @classmethod
    def from_aron(cls, dto: "armarx.aron.data.dto.GenericData"):
        from armarx_memory.aron.conversion import from_aron

        d = from_aron(dto)
        return cls(**d)


class PersonInstanceClientBase:

    core_segment_id = MemoryID("Human", "PersonInstance")

    def __init__(self):
        pass

    def make_entity_name(
        self, provider_name: str, entity_name: str = "person_instance"
    ):
        return self.core_segment_id.with_provider_segment_name(
            provider_name
        ).with_entity_name(entity_name)


class PersonInstanceWriter(PersonInstanceClientBase):
    def __init__(self, writer: Writer):
        super().__init__()
        self.writer = writer

    @classmethod
    def from_mns(cls, mns: MemoryNameSystem, wait=True) -> "PersonInstanceWriter":
        return cls(
            mns.wait_for_writer(cls.core_segment_id)
            if wait
            else mns.get_writer(cls.core_segment_id)
        )

    def commit(
        self,
        entity_id: MemoryID,
        personID: MemoryID,
        pose: np.ndarray,
        time_created_usec=None,
        **kwargs
    ):
        person_instance = PersonInstance(personID=personID, pose=pose)
        commit = Commit()
        commit.add(
            entity_id=entity_id,
            time_created_usec=time_created_usec,
            instances_data=[person_instance.to_aron()],
            **kwargs
        )
        return self.writer.commit(commit)


class PersonInstanceReader(PersonInstanceClientBase):
    def __init__(self, reader: Reader):
        super().__init__()
        self.reader = reader

    def fetch_latest_instance(self, updated_ids: Optional[List[MemoryID]] = None):
        """
        Query the latest snapshot of the given updated IDs and
        return its first instance.
        """
        if updated_ids is None:
            memory = self.reader.query_latest(self.core_segment_id)

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
            latest_snapshot = self.reader.query_snapshot(latest_snapshot_id)

        if not latest_snapshot:
            return None

        latest_instance = latest_snapshot.instances[0]
        return latest_instance

    @classmethod
    def from_mns(cls, mns: MemoryNameSystem, wait=True) -> "PersonInstanceReader":
        return cls(
            mns.wait_for_reader(cls.core_segment_id)
            if wait
            else mns.get_reader(cls.core_segment_id)
        )
