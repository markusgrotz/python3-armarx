from .dataclass_from_to_aron_ice import dataclass_from_aron_ice, dataclass_to_aron_ice
from .options import ConversionOptions


def to_aron(value) -> "armarx.aron.data.dto.GenericData":
    from armarx_memory.aron.aron_dataclass import AronDataclass

    if isinstance(value, AronDataclass):
        return value.to_aron_ice()
    else:
        from .pythonic_from_to_aron_ice import pythonic_to_aron_ice

        return pythonic_to_aron_ice(value)


def from_aron(data: "armarx.aron.data.dto.GenericData"):
    from .pythonic_from_to_aron_ice import pythonic_from_aron_ice

    return pythonic_from_aron_ice(data)
