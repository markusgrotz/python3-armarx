from typing import Union, List, Dict, Any


class IceTwin:
    """
    A python class representing a python-twin of an class defined in Ice.

    Hint: Kind of deprecated. Use IceConverter from armarx.ice_conv.ice_converter instead.

    Usage:

    class MyClass(IceTwin):  # Derive from IceTwin

        def __init__(self, data: int):
            self.data = data


        # Override _protected functions

        @classmethod
        def _get_ice_cls(cls):
            return armarx.dto.MyClass

        def _set_from_ice(self, dto: armarx.dto.MyClass):
            self.data = dto.data

        def _set_to_ice(self, dto: armarx.dto.MyClass):
            dto.data = self.data
    """

    @classmethod
    def from_ice(cls, ice):
        if isinstance(ice, list):
            return list(map(cls.from_ice, ice))
        elif isinstance(ice, dict):
            return {k: to_ice(v) for k, v in ice.items()}
        else:
            self = cls()
            self._set_from_ice(ice)
            return self

    def to_ice(self):
        cls = self._get_ice_cls()
        ice = cls()
        self._set_to_ice(ice)
        return ice

    def set_from_ice(self, dto):
        self._set_from_ice(dto)

    def set_to_ice(self, dto):
        self._set_to_ice(dto)

    @classmethod
    def _get_ice_cls(cls):
        """Return the Ice DTO class."""
        raise NotImplementedError(
            f"{cls.__name__} does not implement `_get_ice_cls()`."
        )

    def _set_from_ice(self, dto):
        """Set `self` from `dto`."""
        raise NotImplementedError(
            f"{self.__class__.__name__} cannot be set from ice. "
            "\nImplement `_set_from_ice()` to allow it."
        )

    def _set_to_ice(self, dto):
        """Set `dto` from `self`."""
        raise NotImplementedError(
            f"{self.__class__.__name__} cannot set to ice. "
            "\nImplement `_set_to_ice()` to allow it.`"
        )


def to_ice(twin: Union[IceTwin, List, Dict]):
    if isinstance(twin, IceTwin):
        return twin.to_ice()
    elif isinstance(twin, list):
        return [to_ice(t) for t in twin]
    elif isinstance(twin, dict):
        return {k: to_ice(t) for k, t in twin.items()}


def __swap_assignments(code: str):
    """
    Helps you write _set_to_ice() after writing _set_from_ice().
    """
    lines = code.splitlines(keepends=False)
    out_lines = []
    for line in lines:
        sides = [s.strip() for s in line.split("=")]
        if len(sides) == 2:
            out_lines.append("{} = {}".format(sides[1], sides[0]))
        else:
            out_lines.append(line)

    print("".join(["{}\n".format(l) for l in out_lines]))
