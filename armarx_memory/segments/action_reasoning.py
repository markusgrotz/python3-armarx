from typing import List
from typing import Optional

import numpy as np

from armarx_memory.core import MemoryID
from armarx_memory.client import Commit

from armarx_memory.segments.base_segment import BaseClient
from armarx_memory.segments.base_segment import BaseReader
from armarx_memory.segments.base_segment import BaseWriter


class Anticipation(object):
    def __init__(self, prediction: List[str]):
        self.prediction = prediction

    def to_aron(self) -> "armarx.aron.data.dto.GenericData":
        from armarx_memory.aron.conversion import to_aron

        return to_aron({"prediction": self.prediction})

    @classmethod
    def from_aron(cls, dto: "armarx.aron.data.dto.GenericData"):
        from armarx_memory.aron.conversion import from_aron

        return cls(**from_aron(dto))


class AnticipationClientBase(BaseClient):

    core_segment_id = MemoryID("Reasoning", "Anticipation")

    default_entity_name = "prediction"


class AnticipationWriter(AnticipationClientBase, BaseWriter):
    pass


class AnticipationReader(AnticipationClientBase, BaseReader):
    pass
