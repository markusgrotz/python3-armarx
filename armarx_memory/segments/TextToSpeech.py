from typing import Dict, List, Optional

from armarx_memory.core import MemoryID
from armarx_memory.client import MemoryNameSystem, Commit, Reader, Writer


class TextToSpeech:
    def __init__(
        self,
        text: str,
    ):
        self.text = text

    def to_aron(self) -> "armarx.aron.data.dto.GenericData":
        from armarx_memory.aron.conversion import to_aron

        dto = to_aron(
            {
                "text": self.text,
            }
        )
        return dto

    @classmethod
    def from_aron(cls, dto: "armarx.aron.data.dto.GenericData"):
        from armarx_memory.aron.conversion import from_aron

        d = from_aron(dto)
        return cls(**d)

    def __repr__(self):
        return "<{c} text='{t}'>".format(c=self.__class__.__name__, t=self.text)


class TextToSpeechClientBase:

    core_segment_id = MemoryID("Speech", "TextToSpeech")

    def __init__(self):
        pass

    def make_entity_name(self, provider_name: str, entity_name: str = "text"):
        return self.core_segment_id.with_provider_segment_name(
            provider_name
        ).with_entity_name(entity_name)


class TextToSpeechWriter(TextToSpeechClientBase):
    def __init__(self, writer: Writer):
        super().__init__()
        self.writer = writer

    @classmethod
    def from_mns(cls, mns: MemoryNameSystem, wait=True) -> "TextToSpeechWriter":
        return cls(
            mns.wait_for_writer(cls.core_segment_id)
            if wait
            else mns.get_writer(cls.core_segment_id)
        )

    def commit(
        self,
        entity_id: MemoryID,
        text: str,
        time_created_usec=None,
        **kwargs,
    ):
        commit = Commit()
        commit.add(
            entity_id=entity_id,
            time_created_usec=time_created_usec,
            instances_data=[TextToSpeech(text=text).to_aron()],
            **kwargs,
        )
        return self.writer.commit(commit)


class TextToSpeechReader(TextToSpeechClientBase):
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

        latest_instance = latest_snapshot.instances[0]
        return latest_instance

    @classmethod
    def from_mns(cls, mns: MemoryNameSystem, wait=True) -> "TextToSpeechReader":
        return cls(
            mns.wait_for_reader(cls.core_segment_id)
            if wait
            else mns.get_reader(cls.core_segment_id)
        )
