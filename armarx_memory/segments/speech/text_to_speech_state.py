import enum

import dataclasses as dc
import typing as ty

from armarx_memory.aron.aron_dataclass import AronDataclass
from armarx_memory.core import MemoryID
from armarx_memory.client.detail import SpecialClientBase as scb


CORE_SEGMENT_ID = MemoryID("Speech", "TextToSpeechState")


@dc.dataclass
class TextToSpeechState(AronDataclass):

    class Event(enum.IntEnum):
        STARTED = 0
        FINISHED = 1

    event: Event
    text: str
    tts_snapshot_id: MemoryID

    core_segment_id: ty.ClassVar[MemoryID] = CORE_SEGMENT_ID

    @classmethod
    def _get_conversion_options(cls) -> ty.Optional["ConversionOptions"]:
        from armarx_memory.aron.conversion.options import ConversionOptions
        return ConversionOptions(
            names_python_to_aron_dict={
                "tts_snapshot_id": "ttsSnapshotID",
            },
        )


class TextToSpeechStateWriter(scb.SpecialWriterBase):
    core_segment_id = CORE_SEGMENT_ID

    @classmethod
    def _get_aron_class(cls):
        return TextToSpeechState

    @classmethod
    def _get_default_core_segment_id(cls):
        return TextToSpeechState.core_segment_id


class TextToSpeechStateReader(scb.SpecialReaderBase):
    core_segment_id = CORE_SEGMENT_ID

    @classmethod
    def _get_aron_class(cls):
        return TextToSpeechState

    @classmethod
    def _get_default_core_segment_id(cls):
        return TextToSpeechState.core_segment_id
