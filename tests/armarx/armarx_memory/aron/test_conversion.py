import pytest

from armarx_memory.aron.common.names import Names
from armarx_memory.aron.conversion import to_aron, from_aron


@pytest.fixture
def names_in():
    return Names(spoken=["spoken"], recognized=["reco1", "reco2"])


def test_names_to_from_aron(names_in: Names):
    aron = to_aron(names_in)
    # print(aron)

    names_out = Names(**from_aron(aron))
    # print(names_out)

    assert names_out.spoken == names_in.spoken
    assert names_out.recognized == names_in.recognized
