import enum
import logging

import dataclasses as dc
import typing as ty
import numpy as np


class DataclassFromToDict:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def _prefix(self, depth: int) -> str:
        return "  " * depth

    def dataclass_from_dict(
            self,
            cls,
            data: ty.Dict,
            depth: int = 0,
    ):
        """
        Deeply converts a dictionary with pythonic data types
        to an instance of the given dataclass.

        :param cls: The dataclass.
        :param data: The data.
        :param depth: The current recursion depth. Only used for logging.
        :return: An instance of the dataclass.
        """
        return self.value_from_pythonic(value_name=None, value_type=cls, value=data, depth=depth)

    def value_from_pythonic(
            self,
            value_name: ty.Optional[str],
            value_type,
            value,
            depth: int,
    ):
        pre = self._prefix(depth)
        try:
            origin = value_type.__origin__
        except AttributeError:
            origin = None

        if self.logger is not None:
            self.logger.debug(
                (f"{pre}- Field '{value_name}':" if value_name is not None
                 else f"{pre}- Value:")
                + f"\n{pre}  - type of annot.: {value_type}"
                + f"\n{pre}  - origin: {origin}"
                + f"\n{pre}  - type of value: {type(value).__name__}"
            )

        if value_type == type(value):
            if self.logger is not None:
                self.logger.debug(f"{pre}> Type matches exactly. Return value {value_type.__name__} as-is.")
            # Nothing to do.
            return value

        if value_type == type(None):
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process NoneType")
            if value is None:
                return None

        if value_type == ty.Any:
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process ty.Any")
            return value

        if origin is not None:
            # Type annotation such as ty.List, ty.Dict, etc.
            if origin in (ty.List, list):
                [vt] = value_type.__args__
                if self.logger is not None:
                    self.logger.debug(f"{pre}> Process ty.List[{vt}] ")
                return [
                    self.value_from_pythonic(value_name=None, value_type=vt, value=v, depth=depth+1)
                    for v in value
                ]

            elif origin in (ty.Dict, dict):
                kt, vt = value_type.__args__
                if self.logger is not None:
                    self.logger.debug(f"{pre}> Process ty.Dict[{kt}, {vt}]")
                return {
                    kt(k): self.value_from_pythonic(value_name=None, value_type=vt, value=v, depth=depth+1)
                    for k, v in value.items()
                }

            elif origin in (ty.Union,):  # Included ty.Optional[]
                union_types = value_type.__args__
                if self.logger is not None:
                    self.logger.debug(f"{pre}> Process ty.Union[{union_types}]")

                if type(None) in union_types and value is None:
                    return None

                for union_type in union_types:
                    if self.logger is not None:
                        self.logger.debug(f"{pre}  - Try union option {union_type} ...")

                    # ToDo: Correctly capture when this conversion fails and proceed with next one.
                    result = self.dataclass_from_dict(union_type, value, depth=depth+1)
                    if isinstance(result, union_type):
                        return result

        # No type from typing.

        # Try ARON data class.
        from armarx_memory.aron.aron_dataclass import AronDataclass
        if issubclass(value_type, AronDataclass):
            conversion_options = value_type._get_conversion_options()
        else:
            conversion_options = None

        if issubclass(value_type, enum.Enum):
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process enum: {value_type}")
            assert isinstance(value, int), value
            return value_type(value)

        try:
            field_types = value_type.__annotations__

        except AttributeError:
            # Not a data class.
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process other type: {value_type}")

            return self.non_dataclass_from_dict(cls=value_type, data=value, depth=depth)

        # Build kwargs for cls.
        kwargs = dict()
        for field_name, value in value.items():
            if conversion_options is not None:
                field_name = conversion_options.name_aron_to_python(field_name)

            try:
                field_type = field_types[field_name]
            except KeyError as e:
                raise KeyError(
                    f"Found no dataclass field '{field_name}' in ARON dataclass {value_type.__name__} matching the data entry. "
                    "Available are: " + ", ".join(f"'{f}'" for f in field_types))

            field_value = self.value_from_pythonic(value_name=field_name, value_type=field_type, value=value, depth=depth)

            kwargs[field_name] = field_value

        # Construct from kwargs and return.
        return value_type(**kwargs)

    def non_dataclass_from_dict(self, cls, data, depth: int):
        # Not a dataclass. Can just try to deliver kwargs. Or return data.

        pre = self._prefix(depth)

        method_name = "from_aron_ice"
        if isinstance(cls.__dict__.get(method_name, None), classmethod):
            if self.logger is not None:
                self.logger.debug(f"{pre}Not a dataclass, but provides method '{method_name}()'.")
            return cls.from_aron_ice(data)

        try:
            result = cls(**data)
        except TypeError:
            if cls == np.ndarray:
                if self.logger is not None:
                    self.logger.debug(f"{pre} is np.ndarray. Return data of type {type(data)} as-is..")
                return data
            try:
                result = cls(data)
            except TypeError:
                if self.logger is not None:
                    self.logger.debug(f"{pre}Not a dataclass. Return data of type  {type(data)} as-is..")
                return data
            else:
                if self.logger is not None:
                    self.logger.debug(f"{pre}Not a dataclass. Construct {cls} from  {type(data)}.")
                return result
        else:
            if self.logger is not None:
                self.logger.debug(f"{pre}Not a dataclass. Construct {cls} from kwargs.")
            return result


    def dataclass_to_dict(
        self,
        obj,
        depth: ty.Optional[int] = 0,
    ) -> ty.Dict[str, ty.Any]:
        """
        Deeply converts an ARON dataclass to a dict.

        :param obj: An object of a dataclass.
        :param depth:
        :return: A dict containing pythonic data types.
        """

        pre = self._prefix(depth)

        from armarx_memory.aron.aron_dataclass import AronDataclass
        if isinstance(obj, AronDataclass):
            conversion_options = obj._get_conversion_options()
        else:
            conversion_options = None

        # Does not respect conversion_options.
        # dc.asdict(obj)

        if self.logger is not None:
            self.logger.debug(f"{pre}Construct dictionary from object of class {obj.__class__.__name__} ...")

        try:
            fields: ty.Iterable[dc.Field] = dc.fields(obj)
        except TypeError:
            # Not a dataclass => return as-is.
            return obj

        # Build kwargs for cls.
        data = dict()
        for field in fields:
            field_name = field.name
            field_type = field.type
            origin = field_type.__dict__.get("__origin__", None)

            if ty.ClassVar in [field_type, origin]:
                continue

            try:
                value = obj.__dict__[field_name]
            except KeyError:
                raise KeyError(f"Field '{field_name}' of type {field_type} (origin: {origin})"
                               f" not found in object of type {type(obj)}."
                               f" Available are: " + ", ".join(f"'{f}'" for f in obj.__dict__.keys()))

            if conversion_options is not None:
                aron_field_name = conversion_options.name_python_to_aron(field_name)
            else:
                aron_field_name = field_name

            field_value = self.field_value_to_pythonic(name=aron_field_name, type_=field_type, value=value, depth=depth)

            data[aron_field_name] = field_value

        return data

    def field_value_to_pythonic(
            self,
            name: str,
            type_,
            value,
            depth: int,
    ):
        pre = self._prefix(depth)
        origin = type_.__dict__.get("__origin__", None)

        if self.logger is not None:
            value_type = type(value)
            self.logger.debug(
                f"{pre}- Field '{name}':"
                f"\n{pre}  - type of annot.: {type_}"
                f"\n{pre}  - origin: {origin}"
                f"\n{pre}  - type of value: {value_type}"
            )

        if value is None:
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process None-cType")

            if origin == ty.Union:
                union_types = type_.__args__
                assert type(None) in union_types, (type_, origin, union_types)
            else:
                assert type_ == type(None), (type_, origin)  # Note, If this fails, comment out

            return None

        elif isinstance(value, list):
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process list ")
            return [self.dataclass_to_dict(v, depth=depth+1) for v in value]

        elif isinstance(value, dict):
            return {k: self.dataclass_to_dict(v, depth=depth + 1) for k, v in value.items()}

        else:
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process other type: {type_}")
            try:
                return self.dataclass_to_dict(value, depth=depth + 1)
            except AttributeError:
                # Cannot convert.
                if self.logger is not None:
                    self.logger.debug(f"{pre}> Not a dataclass. Return value {value} as-is..")
                return value


def dataclass_to_dict(
    obj,
    logger: ty.Optional[logging.Logger] = None,
) -> ty.Dict[str, ty.Any]:
    """
    Deeply converts a dataclass to a dict.

    :param obj: An object of an ARON dataclass.
    :param logger: An optional logger.
    :return: A dict containing pythonic data types.
    """

    converter = DataclassFromToDict(logger=logger)
    return converter.dataclass_to_dict(obj=obj)


def dataclass_from_dict(
    cls,
    data: ty.Dict,
    logger: ty.Optional[logging.Logger] = None,
):
    """
    Deeply converts a dictionary with pythonic data types
    to an instance of the given ARON dataclass.

    :param cls: The dataclass.
    :param data: The data.
    :param logger: A logger.
    :return: An instance of the dataclass.
    """

    converter = DataclassFromToDict(logger=logger)
    return converter.dataclass_from_dict(cls=cls, data=data)
