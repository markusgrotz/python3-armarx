import typing as ty

import armarx
from armarx_memory import client as amc


class EntityStream:

    def __init__(
            self,
    ):
        from armarx_core.time.date_time import DateTimeIceConverter
        self._time_conv = DateTimeIceConverter()
        self._stop = False

    def open(
            self,
            reader: amc.Reader,
            entity_id: amc.MemoryID,
            memory_callback: ty.Callable[[armarx.armem.data.Memory], bool],
            poll_rate_hz=10,
    ):
        from armarx_core.tools.metronome import Metronome
        from armarx_core.time.date_time import time_usec

        metronome = Metronome(frequency_hertz=poll_rate_hz)
        time_start = time_usec()

        while not self._stop:
            metronome.wait_for_next_tick()
            time_end = time_usec()

            def make_query():
                import armarx.armem.query.data as qd

                q_entity = qd.entity.TimeRange(
                    minTimestamp=self._time_conv.to_ice(time_start),
                    maxTimestamp=self._time_conv.to_ice(time_end),
                )
                q_prov = qd.provider.Single(
                    entityName=entity_id.entity_name,
                    entityQueries=[q_entity])
                q_core = qd.core.Single(
                    providerSegmentName=entity_id.provider_segment_name,
                    providerSegmentQueries=[q_prov],
                )
                q_memory = qd.memory.Single(
                    coreSegmentName=entity_id.core_segment_name,
                    coreSegmentQueries=[q_core],
                )
                return [q_memory]

            query = make_query()
            memory_data = reader.query(query)

            # Get timestamps.
            last_timestamp: ty.Optional[int] = None
            max_timestamp: ty.Optional[int] = None

            def process_instance_data(id_: amc.MemoryID, data_: ty.Dict):
                nonlocal last_timestamp, max_timestamp
                if last_timestamp is None:
                    last_timestamp = id_.timestamp_usec
                else:
                    assert last_timestamp < id_.timestamp_usec, (
                        f"Instances must be processed in order of timestamps, but {last_timestamp} >= "
                        f"{id_.timestamp_usec}")

                if max_timestamp is None:
                    max_timestamp = id_.timestamp_usec
                else:
                    max_timestamp = max(max_timestamp, id_.timestamp_usec)

            reader.for_each_instance_data(process_instance_data, memory_data)

            if max_timestamp is not None:
                time_start = max_timestamp + 1

            continue_ = memory_callback(memory_data)

            if not continue_:
                self._stop = True
