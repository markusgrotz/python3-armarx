import enum
from typing import Dict, List, Optional

from armarx.aronpy import conversion as aronconv

from armarx.mem.core import MemoryID
from armarx.mem.client.detail import SpecialClientBase as scb


class TextToSpeechStateWriter(scb.SpecialWriterBase):

    @classmethod
    def _get_aron_class(cls):
        return TextToSpeechState

    @classmethod
    def _get_default_core_segment_id(cls):
        return TextToSpeechState.core_segment_id


class TextToSpeechStateReader(scb.SpecialReaderBase):

    @classmethod
    def _get_aron_class(cls):
        return TextToSpeechState

    @classmethod
    def _get_default_core_segment_id(cls):
        return TextToSpeechState.core_segment_id



class TextToSpeechEvent(enum.IntEnum):
    STARTED = 0
    FINISHED = 1


class TextToSpeechState:

    core_segment_id = MemoryID("Speech", "TextToSpeechState")
    Type = TextToSpeechStateType
    Reader = TextToSpeechStateReader
    Writer = TextToSpeechStateWriter

    def __init__(
            self,
            event: TextToSpeechEvent,
            text: str,
            tts_snapshot_id: MemoryID,
            ):
        self.event = event
        self.text = text
        self.tts_snapshot_id = tts_snapshot_id

    def to_aron(self) -> "armarx.aron.data.AronData":
        dto = aronconv.to_aron({
            "event": self.event,
            "text": self.text,
            "ttsSnapshotID": self.tts_snapshot_id,
        })
        return dto

    @classmethod
    def from_aron(cls, dto: "armarx.aron.data.AronData"):
        d = aronconv.from_aron(dto)
        d["tts_snapshot_id"] = d.pop("ttsSnapshotID")
        return cls(**d)

    def __repr__(self):
        return "<{c} event='{e}' tts ID={tts} text={text}>".format(
            c=self.__class__.__name__,
            e=self.event,
            tts=self.tts_snapshot_id,
            text=self.text,
        )
