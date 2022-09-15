import enum
import dataclasses as dc
import typing as ty

from armarx_memory.aron.aron_dataclass import AronDataclass
from armarx_memory.aron.common.names import Names
from armarx_memory.aron.common.package_path import PackagePath
from armarx_memory.client import MemoryNameSystem, Commit, Reader, Writer
from armarx_memory.core import MemoryID


class Gender(enum.IntEnum):
    DIVERSE = 0
    FEMALE = 1
    MALE = 2


class Handedness(enum.IntEnum):
    BOTH = 0
    LEFT = 1
    RIGHT = 2


@dc.dataclass
class Profile(AronDataclass):

    first_name: str = ""
    last_name: str = ""

    names: Names = Names()

    gender: Gender = Gender.DIVERSE
    handedness: Handedness = Handedness.BOTH

    face_image_paths: ty.List[PackagePath] = dc.field(default_factory=list)
    birthday: int = -1

    height_in_mm: int = -1
    weight_in_g: int = -1

    favourite_color: ty.Tuple[int, int, int] = (192, 192, 192)

    roles: ty.List[str] = dc.field(default_factory=list)

    attributes: ty.Dict[str, ty.Any] = dc.field(default_factory=dict)

    @classmethod
    def _get_conversion_options(cls):
        from armarx_memory.aron.conversion import ConversionOptions

        return ConversionOptions(
            names_snake_case_to_camel_case=True,
            names_python_to_aron_dict={
                "height_in_mm": "heightInMillimeters",
                "weight_in_g": "weightInGrams",
            },
        )


class ProfileClientBase:

    core_segment_id = MemoryID("Human", "Profile")

    def __init__(self):
        pass

    def make_entity_name(self, provider_name: str, entity_name: str):
        return self.core_segment_id.with_provider_segment_name(
            provider_name
        ).with_entity_name(entity_name)


class ProfileWriter(ProfileClientBase):
    def __init__(self, writer: Writer):
        super().__init__()
        self.writer = writer

    @classmethod
    def from_mns(cls, mns: MemoryNameSystem, wait=True) -> "ProfileWriter":
        return cls(
            mns.wait_for_writer(cls.core_segment_id)
            if wait
            else mns.get_writer(cls.core_segment_id)
        )

    def commit(
        self, entity_id: MemoryID, profile: Profile, time_created_usec=None, **kwargs
    ):
        commit = Commit()
        commit.add(
            entity_id=entity_id,
            time_created_usec=time_created_usec,
            instances_data=[profile.to_aron_ice()],
            **kwargs,
        )
        return self.writer.commit(commit)


class ProfileReader(ProfileClientBase):
    def __init__(self, reader: Reader):
        super().__init__()
        self.reader = reader

    @classmethod
    def from_mns(cls, mns: MemoryNameSystem, wait=True) -> "ProfileReader":
        return cls(
            mns.wait_for_reader(cls.core_segment_id)
            if wait
            else mns.get_reader(cls.core_segment_id)
        )

    def query_latest(self) -> ty.Dict[MemoryID, Profile]:
        result = self.reader.query_core_segment(
            self.core_segment_id.core_segment_name, latest_snapshot=True
        )

        id_to_person = {}

        def from_aron(id: MemoryID, aron_data):
            id_to_person[id] = Profile.from_aron_ice(aron_data)

        self.reader.for_each_instance_data(from_aron, result)
        return id_to_person

    def fetch_latest_instance(
        self,
        updated_ids: ty.Optional[ty.List[MemoryID]] = None,
    ):
        if updated_ids is None:
            memory = self.reader.query_latest(self.core_segment_id)

            latest_snapshot = None

            core_seg = memory.coreSegments[self.core_segment_id.core_segment_name]
            for prov_seg in core_seg.providerSegments.values():
                for entity in prov_seg.entities.values():
                    for snapshot in entity.history.values():
                        if latest_snapshot is None:
                            latest_snapshot = snapshot
                        elif (
                            latest_snapshot.id.timestampMicroSeconds
                            < snapshot.id.timestampMicroSeconds
                        ):
                            latest_snapshot = snapshot
        else:
            for up_id in updated_ids:
                assert self.core_segment_id.contains(up_id)

            latest_snapshot_id = max(updated_ids, key=lambda i: i.timestamp_usec)
            latest_snapshot = self.reader.query_snapshot(latest_snapshot_id)

        if not latest_snapshot:
            return None

        latest_instance = latest_snapshot.instances[0]
        return latest_instance
