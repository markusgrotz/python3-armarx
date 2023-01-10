import typing as ty

from armarx_memory.aron.aron_ice_types import AronIceTypes
from armarx_memory.core.MemoryID import MemoryID
from armarx_memory.core.time.date_time import DateTime


class MemoryItem:
    def __init__(
            self,
            id: MemoryID,
    ):
        self.id = id


class EntityInstanceMetadata:

    def __init__(
            self,
            time_created: DateTime = None,
            time_sent: DateTime = None,
            time_arrived: DateTime = None,
            confidence: float = 1.0,
    ):
        self.time_created = time_created if time_created is not None else DateTime()
        self.time_sent = time_sent if time_sent is not None else DateTime()
        self.time_arrived = time_arrived if time_arrived is not None else DateTime()
        self.confidence = confidence


class EntityInstance(MemoryItem):

    Metadata = EntityInstanceMetadata
    Data = AronIceTypes.Dict

    def __init__(
            self,
            id: MemoryID,
            data: ty.Optional[Data] = None,
            metadata: ty.Optional[Metadata] = None,
            instance_index: ty.Optional[int] = None,
    ):
        """
        Construct a new entity instance.
        :param id: The instance's id. If `instance_index` is given, this is the parent snapshot's ID.
        :param data: The data.
        :param metadata: The metadata.
        :param instance_index: The instance index if `id` is the parent snapshot's ID.
        """
        super().__init__(id=id if instance_index is None else id.with_instance_index(instance_index))

        self.metadata = metadata if metadata is not None else self.Metadata()
        self.data = data if data is not None else self.Data()


class EntitySnapshot(MemoryItem):

    def __init__(
            self,
            id: MemoryID,
            timestamp: DateTime = None,
    ):
        super().__init__(id=id if timestamp is None else id.with_timestamp(timestamp.time_since_epoch.to_microseconds()))
        self._children: ty.List[EntityInstance] = list()


class Entity(MemoryItem):

    def __init__(
            self,
            id: MemoryID,
            name: str = None,
    ):
        super().__init__(id=id if name is None else id.with_entity_name(name))
        self._children: ty.Dict[DateTime, EntityInstance] = dict()


class ProviderSegment(MemoryItem):

    def __init__(
            self,
            id: MemoryID,
            name: str = None,
    ):
        super().__init__(id=id if name is None else id.with_provider_segment_name(name))
        self._children: ty.Dict[str, Entity] = dict()


class CoreSegment(MemoryItem):

    def __init__(
            self,
            id: MemoryID,
            name: str = None,
    ):
        super().__init__(id=id if name is None else id.with_core_segment_name(name))
        self._children: ty.Dict[str, ProviderSegment] = dict()


class Memory(MemoryItem):

    def __init__(
            self,
            name_or_id: ty.Union[MemoryID, str],
    ):
        if isinstance(name_or_id, str):
            id = MemoryID(memory_name=name_or_id)
        else:
            assert isinstance(name_or_id, MemoryID)
            id: MemoryID = name_or_id

        super().__init__(id=id)
        self._children: ty.Dict[str, CoreSegment] = dict()
