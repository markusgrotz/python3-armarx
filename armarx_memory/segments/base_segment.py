from abc import ABC
from abc import abstractmethod

from typing import List
from typing import Optional


from armarx_memory.core import MemoryID
from armarx_memory.client import MemoryNameSystem
from armarx_memory.client import Commit
from armarx_memory.client import Reader
from armarx_memory.client import Writer


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
        return (self.core_segment_id.with_provider_segment_name(provider_name)
                .with_entity_name(entity_name))

    @classmethod
    def from_mns(cls, mns: MemoryNameSystem, wait=True):
        if wait:
            mns_proxy = mns.wait_for_reader(cls.core_segment_id)
        else:
            mns_proxy = mns.get_reader(cls.core_segment_id)
        return cls(mns_proxy)




