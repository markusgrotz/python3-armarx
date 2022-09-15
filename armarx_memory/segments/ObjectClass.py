from typing import List
from typing import Optional

from armarx_memory.core import MemoryID

from armarx_memory.segments.base_segment import BaseClient
from armarx_memory.segments.base_segment import GenericDataClass
from armarx_memory.segments.base_segment import BaseReader
from armarx_memory.segments.base_segment import BaseWriter


class ObjectClassClientBase(BaseClient):

    core_segment_id = MemoryID("Object", "Class").with_provider_segment_name(
        "PriorKnowledgeData"
    )

    default_entity_name = "object_class"


class ObjectClassReader(BaseReader, ObjectClassClientBase):
    pass
