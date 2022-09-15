import dataclasses as dc
import typing as ty


@dc.dataclass
class ConversionOptions:
    # Explicit translations from python variable names to Aron names.
    names_python_to_aron_dict: ty.Dict[str, str] = dc.field(default_factory=dict)

    # If true, convert variable names from snake_case (python) to camelCase (Aron).
    names_snake_case_to_camel_case: bool = False

    def name_python_to_aron(self, python_name: str) -> str:
        aron_name = self.names_python_to_aron_dict.get(python_name, None)

        if aron_name is None:
            if self.names_snake_case_to_camel_case:
                from .name_conversion import snake_case_to_camel_case

                aron_name = snake_case_to_camel_case(python_name)
            else:
                aron_name = python_name

        return aron_name

    def name_aron_to_python(self, aron_name: str) -> str:
        for python, aron in self.names_python_to_aron_dict.items():
            if aron == aron_name:
                return python

        if self.names_snake_case_to_camel_case:
            from .name_conversion import camel_case_to_snake_case

            python_name = camel_case_to_snake_case(aron_name)
        else:
            python_name = aron_name

        return python_name
