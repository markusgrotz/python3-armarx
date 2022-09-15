import abc

from typing import ClassVar, Optional

from armarx_memory.core import MemoryID
from armarx_memory.client import MemoryNameSystem, Reader, Writer, Commit, EntityUpdate


class SpecialClientBase(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def _get_default_core_segment_id(cls) -> MemoryID:
        pass

    @classmethod
    @abc.abstractmethod
    def _get_aron_class(cls) -> ClassVar:
        pass


class SpecialWriterBase(SpecialClientBase):
    def __init__(
        self,
        writer: Writer,
        core_segment_id: Optional[MemoryID] = None,
    ):
        self.writer = writer
        self.core_segment_id = core_segment_id or self._get_default_core_segment_id()

    @classmethod
    def from_mns(
        cls,
        mns: MemoryNameSystem,
        wait=True,
        core_segment_id: Optional[MemoryID] = None,
    ):
        if core_segment_id is None:
            core_segment_id = cls._get_default_core_segment_id()
        return cls(
            mns.wait_for_writer(core_segment_id)
            if wait
            else mns.get_writer(core_segment_id)
        )

    def commit(
        self,
        entity_id: MemoryID,
        time_created_usec: Optional[int] = None,
        confidence: Optional[float] = None,
        **data_kwargs,
    ):

        commit = Commit()
        commit.add(
            self.make_update(
                entity_id=entity_id,
                time_created_usec=time_created_usec,
                confidence=confidence,
                **data_kwargs,
            )
        )
        return self.writer.commit(commit)

    def make_update(
        self,
        provider_name: Optional[str] = None,
        entity_name: Optional[str] = None,
        entity_id: Optional[MemoryID] = None,
        time_created_usec: Optional[int] = None,
        confidence: Optional[float] = None,
        data=None,
        **data_kwargs,
    ) -> EntityUpdate:

        if entity_id is None:
            entity_id = self.core_segment_id.with_provider_segment_name(
                provider_name
            ).with_entity_name(entity_name)

        if data is None:
            aron_class = self._get_aron_class()
            data = [aron_class(**data_kwargs).to_aron()]
        if not isinstance(data, list):
            data = [data]
        for i in range(len(data)):
            try:
                data[i] = data[i].to_aron()
            except AttributeError:
                pass

        return EntityUpdate(
            entity_id=entity_id,
            time_created_usec=time_created_usec,
            confidence=confidence,
            instances_data=data,
        )


class SpecialReaderBase(SpecialClientBase):
    def __init__(
        self,
        reader: Reader,
        core_segment_id: Optional[MemoryID] = None,
    ):
        self.reader = reader
        self.core_segment_id = core_segment_id or self._get_default_core_segment_id()

    @classmethod
    def from_mns(
        cls,
        mns: MemoryNameSystem,
        wait=True,
        core_segment_id: Optional[MemoryID] = None,
    ):
        if core_segment_id is None:
            core_segment_id = cls._get_default_core_segment_id()
        return cls(
            mns.wait_for_reader(core_segment_id)
            if wait
            else mns.get_reader(core_segment_id)
        )
