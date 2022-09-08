import pytest

import dataclasses as dc
import typing as ty

from armarx_memory.aron.aron_dataclass import AronDataclass


@dc.dataclass
class Names(AronDataclass):

    spoken: ty.List[str] = dc.field(default_factory=list)
    recognized: ty.List[str] = dc.field(default_factory=list)


@pytest.fixture
def names_in():
    return Names(spoken=["spoken"], recognized=["reco1", "reco2"])


def test_names_to_from_aron(names_in: Names):
    print(f"Input:\n{names_in}")

    aron_ice = names_in.to_aron_ice()
    print(f"Aron ice:\n{aron_ice}")

    names_out = Names.from_aron_ice(aron_ice)
    print(f"Output\n{names_out}")

    assert names_out.spoken == names_in.spoken
    assert names_out.recognized == names_in.recognized
