#!/usr/bin/env python3

from typing import Any, Dict, List

from armarx_memory.aron import conversion as aron_conv
from armarx_memory import core as mem, client as memcl


def print_title(title: str):
    hline = "-" * (len(title))
    print(f"{hline}\n{title}\n{hline}")


def read(core_segment_id: mem.MemoryID):
    # Get Reader.
    example_reader = mns.wait_for_reader(core_segment_id)

    # Perform query.
    memory = example_reader.query_core_segment(
        name=core_segment_id.core_segment_name, latest_snapshot=True
    )

    result_data = None

    # Process result.
    for prov in memory.coreSegments["ExampleData"].providerSegments.values():
        for entity in prov.entities.values():
            for snapshot in entity.history.values():
                for instance in snapshot.instances:
                    # Process entity instance.

                    instance_id = mem.MemoryID.from_ice(instance.id)

                    print_title(f"Instance {instance_id}:")

                    data: Dict[str, Any] = aron_conv.from_aron(instance.data)
                    # Print data.
                    for k, v in data.items():
                        print(f"- '{k}' ({type(v)}):\n{v}")
                    print("")

                    # Return the latest data, just as an example.
                    result_data = data

    return result_data


def write(entity_id: mem.MemoryID, instances_data: List[Dict]):
    # Get Writer.
    example_writer = mns.wait_for_writer(memory_id)

    # Prepare the commit.
    commit = memcl.Commit()
    now = mem.time_usec()

    # Add a snapshot.
    commit.add(
        memcl.EntityUpdate(
            entity_id=entity_id,
            referenced_time_usec=now,
            instances_data=[aron_conv.to_aron(data) for data in instances_data],
        )
    )
    print(commit.updates[-1].instances_data)

    # Perform the commit.
    results = example_writer.commit(commit)

    # Check results.
    print_title(f"Commit results:")
    for result in results.results:
        print(f"- Success: {result.success}, error message: '{result.errorMessage}'")


if __name__ == "__main__":
    """
    In the Scenario Manager:
    - Start the scenario "ArMemCore"
    - From the scenario "ArMemExample":
      - Start the component "ExampleMemory" (RobotAPI)
      - Start the component "ExampleMemoryClient" (RobotAPI)

    Open the GUI plugin "ArMem.MemoryViewer"
    - Check "Auto Update"
    """

    tag = "memory_client_example"

    # Get the Memory Name System.
    mns = memcl.MemoryNameSystem.wait_for_mns()

    # Specify which memory / core segment / ... you want to deal with.
    memory_id = mem.MemoryID("Example")
    core_segment_id = memory_id.with_core_segment_name("ExampleData")

    # Read
    example_data = read(core_segment_id=core_segment_id)

    # Modify the data.
    example_data["the_string"] = "Hello, this string is from python!"
    example_data["the_int"] = 42

    # Write
    entity_id = core_segment_id.with_provider_segment_name(tag).with_entity_name(
        "from_python"
    )
    write(entity_id=entity_id, instances_data=[example_data])

    """
    The MemoryViewer should now show a new entity "from_python" in the 
    provider segment "memory_client_example".
    """

    """
    Have a look at 
    armarx_memory.segments
    where python classes have already been implemented for some modalities.
    
    For example:
    """
    from armarx_memory.segments import ObjectInstance
