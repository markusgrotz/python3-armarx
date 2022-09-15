from typing import Dict, Any, List, Optional, Callable, Union

import armarx.armem as armem

from armarx_memory.core import MemoryID, time_usec
from armarx_memory.client.Commit import Commit, EntityUpdate


class Writer:

    WritingMemoryServerPrx = "armarx.armem.server.WritingMemoryInterfacePrx"

    def __init__(
        self,
        server: Optional[WritingMemoryServerPrx] = None,
    ):
        self.server = server

    def add_provider_segment(
        self,
        provider_id: MemoryID,
        clear_when_exists=False,
    ):

        inp = armem.data.AddSegmentInput()
        inp.coreSegmentName = provider_id.core_segment_name
        inp.providerSegmentName = provider_id.provider_segment_name
        inp.clearWhenExists = clear_when_exists
        results = self.server.addSegments([inp])
        return results[0]

    def commit(
        self,
        commit: Commit,
    ):

        time_sent = time_usec()
        for update in commit.updates:
            update.time_sent_usec = time_sent

        ice_commit = commit.to_ice()

        ice_result = self.server.commit(ice_commit)

        return ice_result

    def __bool__(self):
        return bool(self.server)
