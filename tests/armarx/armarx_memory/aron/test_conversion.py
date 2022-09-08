import pytest

import dataclasses as dc
import numpy as np
import typing as ty

from armarx_memory.aron.aron_dataclass import AronDataclass


@dc.dataclass
class Names(AronDataclass):

    spoken: ty.List[str] = dc.field(default_factory=list)
    recognized: ty.List[str] = dc.field(default_factory=list)

    @classmethod
    def make_test_data(cls) -> "Names":
        return cls(spoken=["spoken"], recognized=["reco1", "reco2"])


@dc.dataclass
class NamedPose(AronDataclass):

    # Re-use another Aron data class.
    names: Names

    position: np.ndarray = dc.field(default_factory=lambda: np.zeros(3, dtype=np.float32))
    orientation: np.ndarray = dc.field(default_factory=lambda: np.array([1., 0., 0., 0.]))

    @classmethod
    def make_test_data(cls) -> "NamedPose":
        return cls(
            names=Names(spoken=["spoken01, spoken02"], recognized=["reco"]),
            position=np.array([1., 2., 3.]),
            orientation=np.array([1., 0., 0., 0.]),
        )


@dc.dataclass
class NativeTypes(AronDataclass):

    string_: str
    bool_: bool
    int_: int
    long_: int
    float_: float

    list_of_ints_: ty.List[int]
    dict_of_floats_: ty.Dict[str, float]

    array_: np.ndarray

    optional_string_: ty.Optional[str] = None

    @classmethod
    def make_test_data(cls, seed=1) -> "NativeTypes":
        return cls(
            string_="forty-two" + str(seed),
            bool_=seed % 2 == 0,
            int_=10 * seed,
            long_=int(1e10) * seed,
            float_=42.5 * seed,

            optional_string_=None if seed % 2 == 1 else "value",

            list_of_ints_=[1, 2, 3] * seed,
            dict_of_floats_={"one": 1.0 * seed, "two": 2.0 * seed, "three-and-a-half": 3.5 * seed},

            array_=np.array([[1, 2, 3], [4, 5, 6]]) * seed,
        )


@dc.dataclass
class ContainersOfDataclasses(AronDataclass):

    list_of_native_types: ty.List[NativeTypes]
    dict_of_native_types: ty.Dict[str, NativeTypes]

    @classmethod
    def make_test_data(cls) -> "ContainersOfDataclasses":
        return cls(
            list_of_native_types=[
                NativeTypes.make_test_data(seed=0),
                NativeTypes.make_test_data(seed=1),
            ],
            dict_of_native_types={
                "one": NativeTypes.make_test_data(seed=1),
                "two": NativeTypes.make_test_data(seed=2),
                "three": NativeTypes.make_test_data(seed=3),
            },
        )


def _test_preamble(cls):
    from armarx_memory.aron.conversion.aron_ice_types import AronIceTypes

    data_in = cls.make_test_data()
    print(f"Input:\n{data_in}")

    aron_ice = data_in.to_aron_ice()
    print(f"Aron ice:\n{aron_ice}")

    assert isinstance(aron_ice, AronIceTypes.Dict)

    data_out = cls.from_aron_ice(aron_ice)
    print(f"Output:\n{data_out}")

    assert isinstance(data_out, cls)

    return data_in, data_out, aron_ice


def test_names_to_from_aron():

    data_in, data_out, aron_ice = _test_preamble(Names)

    assert data_out == data_in
    assert data_out.spoken == data_in.spoken
    assert data_out.recognized == data_in.recognized


def test_named_pose_to_from_aron():
    data_in, data_out, aron_ice = _test_preamble(NamedPose)

    assert isinstance(data_out.position, np.ndarray)
    assert isinstance(data_out.orientation, np.ndarray)
    assert isinstance(data_out.names, Names)

    # Does not work due to numpy arrays.
    # assert data_out == named_pose_in

    assert np.isclose(np.linalg.norm(data_out.position - data_in.position), 0)
    assert np.isclose(np.linalg.norm(data_out.orientation - data_in.orientation), 0)

    assert data_out.names == data_in.names
    assert data_out.names.spoken == data_in.names.spoken
    assert data_out.names.recognized == data_in.names.recognized


def test_native_types_to_from_aron():
    data_in, data_out, aron_ice = _test_preamble(NativeTypes)
    data_out: NativeTypes

    # Test types.
    assert isinstance(data_out.string_, str)
    assert isinstance(data_out.bool_, bool)
    assert isinstance(data_out.int_, int)
    assert isinstance(data_out.long_, int)
    assert isinstance(data_out.float_, float)

    assert isinstance(data_out.list_of_ints_, list)
    assert isinstance(data_out.list_of_ints_[0], int)

    assert isinstance(data_out.dict_of_floats_, dict)
    assert isinstance(next(iter(data_out.dict_of_floats_.values())), float)

    assert isinstance(data_out.array_, np.ndarray)

    assert data_out.optional_string_ is None

    # Test values.
    assert data_out.string_ == data_in.string_
    assert data_out.bool_ == data_in.bool_
    assert data_out.int_ == data_in.int_
    assert data_out.long_ == data_in.long_
    assert data_out.float_ == data_in.float_

    assert data_out.list_of_ints_ == data_in.list_of_ints_
    assert data_out.dict_of_floats_ == data_in.dict_of_floats_

    assert np.all(np.isclose(data_out.array_, data_in.array_))

    assert data_out.optional_string_ is None


def test_containers_of_native_types_to_from_aron():
    data_in, data_out, aron_ice = _test_preamble(ContainersOfDataclasses)
    data_out: ContainersOfDataclasses

    assert isinstance(data_out.list_of_native_types, list)
    assert isinstance(data_out.list_of_native_types[0], NativeTypes)

    assert isinstance(data_out.dict_of_native_types, dict)
    assert isinstance(next(iter(data_out.dict_of_native_types.values())), NativeTypes)
