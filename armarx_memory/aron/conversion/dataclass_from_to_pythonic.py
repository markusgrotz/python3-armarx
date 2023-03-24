import logging

import typing as ty

from armarx_memory.aron.conversion.options import ConversionOptions


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

        pre = self._prefix(depth)

        if self.logger is not None:
            self.logger.debug(f"{pre}Construct value of type {cls.__name__} from a {type(data)} ...")

        if cls == type(data):
            if self.logger is not None:
                self.logger.debug(f"{pre}> Type matches exactly. Return data {cls.__name__} as-is.")
            # Nothing to do.
            return data

        from armarx_memory.aron.aron_dataclass import AronDataclass
        if issubclass(cls, AronDataclass):
            conversion_options = cls._get_conversion_options()
        else:
            conversion_options = None

        try:
            field_types = cls.__annotations__
        except AttributeError:
            return self.non_dataclass_from_dict(cls=cls, data=data, depth=depth)

        # Build kwargs for cls.
        kwargs = dict()
        for field_name, value in data.items():
            if conversion_options is not None:
                field_name = conversion_options.name_aron_to_python(field_name)

            try:
                field_type = field_types[field_name]
            except KeyError as e:
                raise KeyError(
                    f"Found no dataclass field '{field_name}' in ARON dataclass {cls} matching the data entry. "
                    "Available are: " + ", ".join(f"'{f}'" for f in field_types))

            field_value = self.field_value_from_pythonic(field_name=field_name, field_type=field_type, value=value, depth=depth)

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


    def field_value_from_pythonic(
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
                f"{pre}- Field '{field_name}':"
                f"\n{pre}  - type of annot.: {field_type}"
                f"\n{pre}  - origin: {origin}"
                f"\n{pre}  - type of value: {value_type}"
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

            if type(None) in union_types and value is None:
                return None

            for union_type in union_types:
                if self.logger is not None:
                    self.logger.debug(f"{pre}  - Try option {union_type} ...")

                # ToDo: Correctly capture when this conversion fails and proceed with next one.
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
                if self.logger is not None:
                    self.logger.debug(f"{pre}> Not a dataclass. Take value {value} as-is..")
                return value

    def dataclass_to_dict(
        self,
        obj,
        depth: ty.Optional[int] = 0,
    ) -> ty.Dict[str, ty.Any]:
        """
        Deeply converts an ARON dataclass to a dict.

        :param obj: An object of a dataclass.
        :param logger: An optional logger.
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

        field_types = obj.__annotations__

        # Build kwargs for cls.
        data = dict()
        for field_name, field_type in field_types.items():
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
                self.logger.debug(f"{pre}> Process NoneType")

            assert type_ == type(None), type_
            return None

        elif isinstance(value, list):
            if self.logger is not None:
                self.logger.debug(f"{pre}> Process list ")
            return [self.dataclass_to_dict(v, depth=depth+1) for v in value]

        elif isinstance(value, dict):
            return {k: self.dataclass_to_dict(v, depth=depth+1) for k, v in value.items()}

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
