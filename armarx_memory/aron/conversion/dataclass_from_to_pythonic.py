import logging

import dataclasses as dc
import typing as ty

from .options import ConversionOptions


def dataclass_to_dict(
    obj,
    logger: ty.Optional[logging.Logger] = None,
) -> ty.Dict[str, ty.Any]:
    """
    Deeply converts a dataclass to a dict.

    :param obj: An object of a dataclass.
    :param logger: An optional logger.
    :return: A dict containing pythonic data types.
    """
    return dc.asdict(obj)


class DataclassFromDict:

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

        pre = self._prefix(depth)

        if self.logger is not None:
            self.logger.debug(f"{pre}Construct value of type {cls.__name__} from a {type(data)} ...")

        if cls == type(data):
            if self.logger is not None:
                self.logger.debug(f"{pre}> Type matches exactly. Return data {cls.__name__} as-is.")

            # Nothing to do.
            return data

        try:
            field_types = cls.__annotations__
        except AttributeError:
            return self.non_dataclass_from_dict(cls=cls, data=data, depth=depth)

        # Build kwargs for cls.
        kwargs = dict()
        for field_name, value in data.items():
            field_type = field_types[field_name]

            field_value = self.get_field_value(field_name=field_name, field_type=field_type, value=value, depth=depth)

            kwargs[field_name] = field_value

        # Construct from kwargs and return.
        return cls(**kwargs)

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
            if self.logger is not None:
                self.logger.debug(f"{pre}Not a dataclass. Return data of type {type(data)} as-is..")
            return data
        else:
            if self.logger is not None:
                self.logger.debug(f"{pre}Not a dataclass. Construct {cls} from kwargs.")
            return result


    def get_field_value(
            self,
            field_name: str,
            field_type,
            value,
            depth: int,
    ):
        pre = self._prefix(depth)

        try:
            origin = field_type.__origin__
        except AttributeError:
            origin = None

        if self.logger is not None:
            value_type = type(value)
            self.logger.debug(
                f"- Field '{field_name}':"
                f"\n  - type of annot.: {field_type}"
                f"\n  - origin: {origin}"
                f"\n  - type of value: {value_type}"
            )

        if field_type == type(None):
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process NoneType")
            if value is None:
                return None

        elif origin in (ty.List, list):
            [vt] = field_type.__args__
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process list of {vt} ")
            return [self.dataclass_from_dict(vt, v, depth=depth+1) for v in value]

        elif origin in (ty.Dict, dict):
            kt, vt = field_type.__args__
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process dict {kt} -> {vt}")
            if value is not None:
                return {
                    kt(k): self.dataclass_from_dict(vt, v, depth=depth+1) for k, v in value.items()
                }
            else:
                return None

        elif origin == ty.Union:
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process union.")

            union_types = field_type.__args__
            for union_type in union_types:
                if self.logger is not None:
                    self.logger.debug(f"{pre}  - Try option {union_type} ...")

                result = self.dataclass_from_dict(union_type, value, depth=depth+1)
                if isinstance(result, union_type):
                    return result

        else:
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process other type: {field_type}")
            try:
                return self.dataclass_from_dict(field_type, value, depth=depth+1)
            except AttributeError:
                # Cannot convert.
                self.logger.debug(f"{pre}> Not a dataclass. Take value {value} as-is..")
                return value


def dataclass_from_dict(
    cls,
    data: ty.Dict,
    logger: ty.Optional[logging.Logger] = None,
):
    """
    Deeply converts a dictionary with pythonic data types
    to an instance of the given dataclass.

    :param cls: The dataclass.
    :param data: The data.
    :param logger: A logger.
    :return: An instance of the dataclass.
    """

    converter = DataclassFromDict(logger=logger)
    return converter.dataclass_from_dict(cls=cls, data=data)
