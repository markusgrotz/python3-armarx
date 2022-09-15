import dataclasses as dc
import typing as ty


@dc.dataclass
class AronDataclass:
    def to_dict(self) -> ty.Dict[str, ty.Any]:
        from armarx_memory.aron.conversion.dataclass_from_to_pythonic import (
            dataclass_to_dict,
        )

        return dataclass_to_dict(self)

    def to_aron_ice(self) -> "armarx.aron.data.dto.Dict":
        from armarx_memory.aron.conversion.dataclass_from_to_aron_ice import (
            dataclass_to_aron_ice,
        )

        return dataclass_to_aron_ice(self, options=self._get_conversion_options())

    @classmethod
    def from_dict(cls, data: ty.Dict[str, ty.Any]) -> "AronDataclass":
        from armarx_memory.aron.conversion.dataclass_from_to_pythonic import (
            dataclass_from_dict,
        )

        return dataclass_from_dict(cls, data)

    @classmethod
    def from_aron_ice(cls, data: "armarx.aron.data.dto.Dict") -> "AronDataclass":
        from armarx_memory.aron.conversion.dataclass_from_to_aron_ice import (
            dataclass_from_aron_ice,
        )

        return dataclass_from_aron_ice(cls, data, options=cls._get_conversion_options())

    @classmethod
    def _get_conversion_options(cls) -> ty.Optional["ConversionOptions"]:
        return None
