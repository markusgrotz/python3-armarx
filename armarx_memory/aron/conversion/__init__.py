from armarx_memory.aron.aron_dataclass import AronDataclass
from .dataclass_from_to_aron_ice import dataclass_from_aron_ice, dataclass_to_aron_ice


def to_aron(value) -> "armarx.aron.data.dto.GenericData":
    if isinstance(value, AronDataclass):
        return value.to_aron_ice()
    else:
        from .pythonic_from_to_ice import pythonic_to_aron
        return pythonic_to_aron(value)


def from_aron(data: "armarx.aron.data.dto.GenericData"):
    from .pythonic_from_to_ice import pythonic_from_aron
    return pythonic_from_aron(data)
