import abc
from typing import Callable, Dict, Type


class IceConverter(abc.ABC):
    """
    Allows to define the conversion between a Python Business Object (BO; i.e. of a python type)
    and an Ice Data Transfer Object (DTO; i.e. an object of classes defined in Ice)
    and provides additional handling for containers of that type.

    Usage:

    class MyClassConv(IceConverter):  # Derive from IceConverter

        # Override _protected functions

        @classmethod
        def _import_dto(cls):
            slice_loader.load_armarx_slice(...)
            return armarx.dto.MyClass

        def _from_ice(self, dto: armarx.dto.MyClass) -> MyClass:
            return MyClass(data=dto.data)

        def _to_ice(self, bo: MyClass) -> armarx.dto.MyClass:
            return MyClass(data=bo.data)


    def foo():
        # Get an Ice DTO from somewhere.
        dto: armarx.dto.MyClass = get_ice_dto()

        # Create the converter and use it to convert the DTO to a BO.
        conv = MyClassConv()
        bo: MyClass = conv.from_ice(dto)

        # Use the same converter to convert the BO back to Ice.
        dto2: armarx.dto.MyClass = conv.to_ice(bo)

        # Use the same methods to convert lists or dictionaries:
        bos = conv.from_ice([dto, dto2])
        ...
    """

    _dto = None

    def __init__(self):
        self._handlers_from_ice: Dict[Type, Callable] = dict()
        self._handlers_to_ice: Dict[Type, Callable] = dict()

        self.set_handler_from_ice(
            list,
            lambda dto, *args, **kwargs: list(
                map(lambda e: self.from_ice(e, *args, **kwargs), dto)
            ),
        )
        self.set_handler_to_ice(
            list,
            lambda bo, *args, **kwargs: list(
                map(lambda e: self.to_ice(e, *args, **kwargs), bo)
            ),
        )

        self.set_handler_from_ice(
            dict,
            lambda dto, *args, **kwargs: {
                k: self.from_ice(v, *args, **kwargs) for k, v in dto.items()
            },
        )
        self.set_handler_to_ice(
            dict,
            lambda bo, *args, **kwargs: {
                k: self.to_ice(v, *args, **kwargs) for k, v in bo.items()
            },
        )

    def from_ice(self, dto, *args, **kwargs):
        """Convert the Ice Data Transfer Object(s) to Python Business Object(s)."""
        for t, handler in self._handlers_from_ice.items():
            if isinstance(dto, t):
                return handler(dto, *args, **kwargs)
        return self._from_ice(dto, *args, **kwargs)

    def to_ice(self, bo, *args, **kwargs):
        """Convert the Python Business Object(s) to Ice Data Transfer Object(s)."""
        for t, handler in self._handlers_from_ice.items():
            if isinstance(bo, t):
                return handler(bo, *args, **kwargs)
        return self._to_ice(bo, *args, **kwargs)

    def set_handler_from_ice(self, type: Type, handler: Callable):
        self._handlers_from_ice[type] = handler

    def set_handler_to_ice(self, type: Type, handler: Callable):
        self._handlers_to_ice[type] = handler

    @classmethod
    def get_dto(cls):
        if cls._dto is None:
            # Dunno why yet, but we need to pass cls explicitly here ...
            try:
                cls._dto = cls._import_dto(cls)
            except TypeError:
                cls._dto = cls._import_dto()
        return cls._dto

    @abc.abstractmethod
    def _from_ice(self, dto, *args, **kwargs):
        """Convert the Ice DTO to a Python BO."""
        ...

    @abc.abstractmethod
    def _to_ice(self, bo, *args, **kwargs):
        """Convert the Python BO to an Ice DTO."""
        ...

    @classmethod
    @abc.abstractmethod
    def _import_dto(cls):
        """Load, import and return the DTO type."""
        ...
