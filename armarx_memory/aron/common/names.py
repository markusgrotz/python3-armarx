import dataclasses as dc
import typing as ty

from armarx_memory.aron.conversion import to_aron, from_aron


@dc.dataclass
class Names:

    spoken: ty.List[str] = dc.field(default_factory=list)
    recognized: ty.List[str] = dc.field(default_factory=list)

    def to_aron(self) -> "armarx.aron.data.dto.GenericData":
        from armarx_memory.aron.dataclasses import dataclass_to_aron
        return dataclass_to_aron(self)

    @classmethod
    def from_aron(cls, dto: "armarx.aron.data.dto.GenericData"):
        from armarx_memory.aron.dataclasses import dataclass_from_aron
        return dataclass_from_aron(cls, dto, verbose=2)
