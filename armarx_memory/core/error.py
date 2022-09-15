from armarx_memory.core.MemoryID import MemoryID


class ArMemError(Exception):
    """Base class for exceptions thrown by armarx.armem."""

    pass


class CouldNotResolveMemoryServer(ArMemError):
    def __init__(self, memory_id: MemoryID, msg: str = ""):
        super().__init__(
            f"Could not resolve the memory name {memory_id}."
            f"\nMemory server for {memory_id} is not registered."
            + ("\n" + msg if msg else "")
        )
