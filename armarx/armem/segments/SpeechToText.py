from typing import Dict, List, Optional

from armarx.aronpy import conversion as aronconv

from armarx.armem.core import MemoryID
from armarx.armem.client import MemoryNameSystem, Commit, Reader, Writer


class SpeechToText:

    def __init__(
            self,
            text: str,
            ):
        self.text = text

    def to_aron(self) -> "armarx.aron.data.AronData":
        dto = aronconv.to_aron({
            "text": self.text,
        })
        return dto

    @classmethod
    def from_aron(cls, dto: "armarx.aron.data.AronData"):
        d = aronconv.from_aron(dto)
        return cls(**d)

    def __repr__(self):
        return "<{c} text='{t}'>".format(
            c=self.__class__.__name__, t=self.text
        )



class SpeechToTextClientBase:

    core_segment_id = MemoryID("Speech", "SpeechToText")

    def __init__(self):
        pass

    def make_entity_name(self, provider_name: str, entity_name: str = "text"):
        return (self.core_segment_id
                .with_provider_segment_name(provider_name)
                .with_entity_name(entity_name))


class SpeechToTextWriter(SpeechToTextClientBase):

    def __init__(self, writer: Writer):
        super().__init__()
        self.writer = writer

    @classmethod
    def from_mns(cls, mns: MemoryNameSystem, wait=True) -> "SpeechToTextWriter":
        return cls(mns.wait_for_writer(cls.core_segment_id)
                   if wait else mns.get_writer(cls.core_segment_id))

    def commit(self,
               entity_id: MemoryID,
               text: str,
               confidence: float,
               time_created_usec = None
               ):
        commit = Commit()
        commit.add(
            entity_id = entity_id,
            time_created_usec=time_created_usec,
            confidence=confidence,
            instances_data=[
                SpeechToText(text=text).to_aron()
            ],
        )
        return self.writer.commit(commit)



class SpeechToTextReader(SpeechToTextClientBase):

    def __init__(self, reader: Reader):
        super().__init__()
        self.reader = reader


    def fetch_latest_instance(self, updated_ids: List[MemoryID]):
        """
        Query the latest snapshot of the given updated IDs and
        return its first instance.
        """
        for up_id in updated_ids:
            assert self.core_segment_id.contains(up_id)

        latest_snapshot_id = max(updated_ids, key=lambda i: i.timestamp_usec)
        latest_snapshot = self.reader.query_snapshot(latest_snapshot_id)
        latest_instance = latest_snapshot.instances[0]
        return latest_instance


    @classmethod
    def from_mns(cls, mns: MemoryNameSystem, wait=True) -> "SpeechToTextReader":
        return cls(mns.wait_for_reader(cls.core_segment_id)
                   if wait else mns.get_reader(cls.core_segment_id))
