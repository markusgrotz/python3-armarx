import time
from typing import Dict, Any, List, Optional, Callable, Union

from armarx import slice_loader
from armarx.ice_manager import get_proxy

slice_loader.load_armarx_slice("RobotAPI", "armem/server/MemoryInterface.ice")
import armarx.aron as aron
import armarx.armem as armem

import verbalmanipulation.ice_conv.IceTwin as icetwin
from .MemoryID import MemoryID


def time_usec() -> int:
    return int(time.time() * 1e6)


def get_memory_proxy(proxy_name: str) -> "armarx.armem.server.MemoryInterfacePrx":
    import Ice
    import logging

    try:
        return get_proxy(armem.server.MemoryInterfacePrx, proxy_name)
    except Ice.NotRegisteredException as e:
        logging.error(e)
        return None


class EntityUpdate(icetwin.IceTwin):

    def __init__(self,
                 entity_id: MemoryID = None,
                 instances_data: List[aron.data.AronData] = None,
                 time_created_usec: Optional[int] = None,
                 confidence: float = 1.0,
                 time_sent_usec: Optional[int] = None):

        self.entity_id: MemoryID = MemoryID() if entity_id is None else entity_id
        self.instances_data = [] if instances_data is None else instances_data

        self.time_created_usec = time_created_usec if time_created_usec is not None else time_usec()

        self.confidence = confidence
        self.time_sent_usec: Optional[int] = None

    def set_time_created_now(self):
        self.time_created_usec = time_usec()

    @classmethod
    def get_ice_cls(cls):
        return armem.data.EntityUpdate

    def set_to_ice(self, ice: armem.data.Commit):
        ice.entityID = self.entity_id.to_ice()
        ice.instancesData = self.instances_data
        ice.timeCreatedMicroSeconds = self.time_created_usec

        ice.confidence = self.confidence
        ice.timeSentMicroSeconds = self.time_sent_usec if self.time_sent_usec is not None else -1

    def set_from_ice(self, ice):
        self.entity_id._set_from_ice(ice.entityID)
        self.instances_data = ice.instancesData
        self.time_created_usec = ice.timeCreatedMicroSeconds

        self.confidence = ice.confidence
        self.time_sent_usec = ice.timeSentMicroSeconds


class Commit(icetwin.IceTwin):

    def __init__(self, updates: List[EntityUpdate] = None):
        self.updates = [] if updates is None else updates

    def get_ice_cls(self):
        return armem.data.Commit

    def set_to_ice(self, ice: armem.data.Commit):
        ice.updates = icetwin.to_ice(self.updates)

    def set_from_ice(self, ice):
        self.updates = EntityUpdate.from_ice(ice.updates)

    def add(self, update: Optional[EntityUpdate] = None):
        if update is None:
            update = EntityUpdate()
        self.updates.append(update)
        return update



class MemoryWriter:

    def __init__(
            self,
            memory_proxy: Optional[armem.server.WritingMemoryInterfacePrx] = None,
            ):
        self.memory_proxy = memory_proxy

    def add_provider_segment(self, provider_id: MemoryID,
                             clear_when_exists=False):
        inp = armem.data.AddSegmentInput()
        inp.coreSegmentName = provider_id.core_segment_name
        inp.providerSegmentName = provider_id.provider_segment_name
        inp.clearWhenExists = clear_when_exists
        results = self.memory_proxy.addSegments([inp])
        return results[0]

    def commit(self, commit: Commit):
        time_sent = time_usec()
        for up in commit.updates:
            up.time_sent_usec = time_sent

        ice_commit = commit.to_ice()

        ice_result = self.memory_proxy.commit(ice_commit)

        return ice_result

    def __bool__(self):
        return self.memory_proxy is not None


class MemoryReader:
    qd = armem.query.data

    Callback = Callable[[MemoryID, List[MemoryID]], None]

    def __init__(
            self,
            memory_proxy: Optional[armem.server.ReadingMemoryInterfacePrx],
            ):
        self.memory_proxy = memory_proxy
        self.subscriptions: Dict[MemoryID, List["MemoryReader.Callback"]] = {}

    def query(self, queries: List[armem.query.data.MemoryQuery]) -> armem.data.Memory:
        inp = self.qd.Input(memoryQueries=queries, withData=True)
        result = self.memory_proxy.query(inp)
        if not result.success:
            raise RuntimeError(f"Memory query failed. Reason:\n{result.errorMessage}")
        else:
            return result.memory


    def query_all(self) -> armem.data.Memory:
        q_entity = self.qd.entity.All()
        q_prov = self.qd.provider.All(entityQueries=[q_entity])
        q_core = self.qd.core.All(providerSegmentQueries=[q_prov])
        q_memory = self.qd.memory.All(coreSegmentQueries=[q_core])
        memory = self.query([q_memory])
        return memory

    def query_core_segment(self,
                           name: str,
                           regex=False,
                           latest_snapshot=False
                           ) -> armem.data.Memory:
        if latest_snapshot:
            q_entity = self.qd.entity.Single()  # Latest
        else:
            q_entity = self.qd.entity.All()
        q_prov = self.qd.provider.All(entityQueries=[q_entity])
        q_core = self.qd.core.All(providerSegmentQueries=[q_prov])
        if regex:
            q_memory = self.qd.memory.Regex(coreSegmentNameRegex=name,
                                            coreSegmentQueries=[q_core])
        else:
            q_memory = self.qd.memory.Single(coreSegmentName=name,
                                             coreSegmentQueries=[q_core])
        memory = self.query([q_memory])
        return memory


    def query_latest(self) -> armem.data.Memory:
        q_entity = self.qd.entity.Single()  # Latest
        q_prov = self.qd.provider.All(entityQueries=[q_entity])
        q_core = self.qd.core.All(providerSegmentQueries=[q_prov])
        q_memory = self.qd.memory.All(coreSegmentQueries=[q_core])
        memory = self.query([q_memory])
        return memory

    def query_snapshot(self, snapshot_id: MemoryID) -> armem.data.EntitySnapshot:
        q_entity = self.qd.entity.Single(timestamp=snapshot_id.timestamp_usec)
        q_prov = self.qd.provider.Single(entityName=snapshot_id.entity_name,
                                         entityQueries=[q_entity])
        q_core = self.qd.core.Single(providerSegmentName=snapshot_id.provider_segment_name,
                                     providerSegmentQueries=[q_prov])
        q_memory = self.qd.memory.Single(coreSegmentName=snapshot_id.core_segment_name,
                                         coreSegmentQueries=[q_core])
        memory = self.query([q_memory])
        snapshot = (memory.coreSegments[snapshot_id.core_segment_name]
                    .providerSegments[snapshot_id.provider_segment_name]
                    .entities[snapshot_id.entity_name]
                    .history[snapshot_id.timestamp_usec]
        )
        return snapshot


    def subscribe(self, id: MemoryID, callback: Callback):
        if id not in self.subscriptions:
            self.subscriptions[id] = [callback]
        else:
            self.subscriptions[id].append(callback)

    def updated(
            self,
            updated_snapshot_ids: List[Union[MemoryID, "armarx.armem.data.MemoryID"]]
            ):
        updated_snapshot_ids: List[MemoryID] = [
            id if isinstance(id, MemoryID) else MemoryID.from_ice(id)
            for id in updated_snapshot_ids
        ]
        for id in updated_snapshot_ids:
            assert isinstance(id, MemoryID)
        for subscribed_id, callbacks in self.subscriptions.items():
            matching_snapshot_ids = [
                updated_snapshot_id for updated_snapshot_id in updated_snapshot_ids
                if subscribed_id.contains(updated_snapshot_id)
            ]
            if len(matching_snapshot_ids) > 0:
                for callback in callbacks:
                    callback(subscribed_id, matching_snapshot_ids)

    def __bool__(self):
        return self.memory_proxy is not None


def __swap_assignments(code: str):
    lines = code.splitlines(keepends=False)
    out_lines = []
    for line in lines:
        sides = [s.strip() for s in line.split("=")]
        if len(sides) == 2:
            out_lines.append("{} = {}".format(sides[1], sides[0]))
        else:
            out_lines.append(line)

    print("".join(["{}\n".format(l) for l in out_lines]))


