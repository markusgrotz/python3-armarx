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

    if logger is not None:
        logger.info(f"\nConstruct class {cls.__name__} from a {type(data)} ...")

    try:
        field_types = cls.__annotations__
    except AttributeError:
        # Not a dataclass. Can just try to deliver kwargs. Or return data.
        try:
            return cls(**data)
        except TypeError:
            return data

    # Build kwargs for cls.
    kwargs = dict()
    for field_name, value in data.items():
        field_type = field_types[field_name]

        try:
            origin = field_type.__origin__
        except AttributeError:
            origin = None

        if logger is not None:
            value_type = type(value)
            logger.debug(
                f"- Field '{field_name}' of type: {field_type}"
                f"\n- origin: {origin}"
                f"\n- data type: {value_type}"
            )

        if origin in (ty.List, list):
            [vt] = field_type.__args__
            if logger is not None:
                logger.debug(f"> Process list of {vt} ")
            field_value = [dataclass_from_dict(vt, v) for v in value]

        elif origin in (ty.Dict, dict):
            kt, vt = field_type.__args__
            if logger is not None:
                logger.debug(f"> Process dict {kt} -> {vt}")
            if value is not None:
                field_value = {
                    kt(k): dataclass_from_dict(vt, v) for k, v in value.items()
                }
            else:
                field_value = None

        else:
            if logger is not None:
                logger.debug(f"> Process other: {field_type}")
            try:
                field_value = dataclass_from_dict(field_type, value)
            except AttributeError:
                # Cannot convert.
                field_value = value

        kwargs[field_name] = field_value

    return cls(**kwargs)
