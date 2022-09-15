import dataclasses as dc
import typing as ty

from armarx_memory.aron.aron_dataclass import AronDataclass


@dc.dataclass
class PackagePath(AronDataclass):

    package: str
    path: str

    def get_system_path(self) -> str:
        import os
        from armarx import cmake_helper

        [data_path] = cmake_helper.get_data_path(self.package)
        abs_path = os.path.join(data_path, self.package, self.path)
        return abs_path
