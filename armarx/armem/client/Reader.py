from typing import Dict, Any, List, Optional, Callable, Union

import armarx.armem as armem

from armarx.armem.core import MemoryID


class Reader:

    ReadingMemoryServerPrx = "armarx.armem.server.ReadingMemoryInterfacePrx"
    qd = armem.query.data


    def __init__(
            self,
            server: Optional[ReadingMemoryServerPrx],
            ):

        self.server = server


    def query(
            self,
            queries: List[armem.query.data.MemoryQuery],
            ) -> armem.data.Memory:

        inp = self.qd.Input(memoryQueries=queries, withData=True)
        result = self.server.query(inp)
        if not result.success:
            raise RuntimeError(f"Memory query failed. Reason:\n{result.errorMessage}")
        else:
            return result.memory


    def query_all(
            self,
            ) -> armem.data.Memory:

        q_entity = self.qd.entity.All()
        q_prov = self.qd.provider.All(entityQueries=[q_entity])
        q_core = self.qd.core.All(providerSegmentQueries=[q_prov])
        q_memory = self.qd.memory.All(coreSegmentQueries=[q_core])
        memory = self.query([q_memory])
        return memory


    def query_core_segment(
            self,
            name: str,
            regex=False,
            latest_snapshot=False,
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


    def query_latest(
            self,
            ) -> armem.data.Memory:

        q_entity = self.qd.entity.Single()  # Latest
        q_prov = self.qd.provider.All(entityQueries=[q_entity])
        q_core = self.qd.core.All(providerSegmentQueries=[q_prov])
        q_memory = self.qd.memory.All(coreSegmentQueries=[q_core])
        memory = self.query([q_memory])
        return memory


    def query_snapshot(
            self,
            snapshot_id: MemoryID,
            ) -> armem.data.EntitySnapshot:

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


    def __bool__(self):
        return bool(self.server)

