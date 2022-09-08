import dataclasses as dc
import typing as ty

from armarx_memory.aron.aron_dataclass import AronDataclass


@dc.dataclass
class Names(AronDataclass):

    spoken: ty.List[str] = dc.field(default_factory=list)
    recognized: ty.List[str] = dc.field(default_factory=list)
