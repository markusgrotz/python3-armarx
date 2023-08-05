import logging

import dataclasses as dc
import typing as ty

from armarx_memory.aron.conversion.options import ConversionOptions


# An ARON-compatible dict. That is, a dictionary that can be con converted to
# and from Ice DTOs.
AronDict = ty.Dict[str, ty.Any]


@dc.dataclass
class AronDataclass:
    # Make ConversionOptions available to subclasses via cls.ConversionOptions.
    ConversionOptions = ConversionOptions

    def to_dict(self) -> AronDict:
        from armarx_memory.aron.conversion import dataclass_from_to_pythonic
        return dataclass_from_to_pythonic.dataclass_to_dict(self)

    def to_aron_ice(
            self,
            logger: logging.Logger = None,
    ) -> "armarx.aron.data.dto.Dict":
        from armarx_memory.aron.conversion import dataclass_from_to_aron_ice
        return dataclass_from_to_aron_ice.dataclass_to_aron_ice(self, logger=logger)

    @classmethod
    def from_dict(
            cls,
            data: AronDict,
            logger: ty.Optional[logging.Logger] = None,
    ) -> "AronDataclass":
        from armarx_memory.aron.conversion.dataclass_from_to_pythonic import (
            dataclass_from_dict,
        )
        return dataclass_from_dict(cls, data, logger=logger)

    @classmethod
    def from_aron_ice(
            cls,
            data: "armarx.aron.data.dto.Dict",
            logger: logging.Logger = None,
    ) -> "AronDataclass":
        from armarx_memory.aron.conversion import dataclass_from_to_aron_ice
        return dataclass_from_to_aron_ice.dataclass_from_aron_ice(cls, aron=data, logger=logger)

    @classmethod
    def _get_conversion_options(cls) -> ty.Optional["ConversionOptions"]:
        return None
