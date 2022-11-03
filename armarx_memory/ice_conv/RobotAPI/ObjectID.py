import os

from armarx_core import slice_loader

from armarx_memory.ice_conv.ice_twin import IceTwin


class ObjectID(IceTwin):
    """
    A Python twin of the Ice DTO class `armarx.data.ObjectID`
    from `ArmarXObjects/ArmarXObjectsTypes.ice` in RobotAPI.
    """

    DEFAULT_PRIOR_KNOWLEDGE_PACKAGE = "PriorKnowledgeData"
    SEP = "/"

    def __init__(self, dataset="", class_name="", instance_name=""):
        self.dataset = dataset
        self.class_name = class_name
        self.instance_name = instance_name

    @classmethod
    def from_str(cls, id: str) -> "ObjectID":
        return cls(*id.split(cls.SEP))

    def get_dir(self, package=DEFAULT_PRIOR_KNOWLEDGE_PACKAGE):
        return os.path.join(package, "objects", self.dataset, self.class_name)

    def get_filename(self, extension: str, suffix=""):
        if not extension.startswith("."):
            extension = "." + extension
        return f"{self.class_name}{suffix}{extension}"

    def get_filepath(
        self,
        extension: str,
        suffix="",
        package=DEFAULT_PRIOR_KNOWLEDGE_PACKAGE,
        resolve=False,
    ):
        filepath = os.path.join(
            self.get_dir(package=package),
            self.get_filename(extension=extension, suffix=suffix),
        )
        return self.resolve_filepath(filepath) if resolve else filepath

    def get_viz_kwargs(self, package=DEFAULT_PRIOR_KNOWLEDGE_PACKAGE, use_wrl=False):
        return dict(
            project=package, filename=self.get_filepath(".wrl" if use_wrl else ".xml")
        )

    @classmethod
    def resolve_filepath(cls, filepath: str):
        from armarx import cmake_helper

        package_name = filepath.split(os.path.sep, maxsplit=1)[0]
        package_data_dir = cmake_helper.get_data_path(package_name)[0]
        return os.path.join(package_data_dir, filepath)

    @classmethod
    def _get_ice_cls(cls):
        slice_loader.load_armarx_slice(
            "RobotAPI", "ArmarXObjects/ArmarXObjectsTypes.ice"
        )
        from armarx.data import ObjectID

        return ObjectID

    def _set_from_ice(self, dto: "armarx.data.ObjectID"):
        self.dataset = dto.dataset
        self.class_name = dto.className
        self.instance_name = dto.instanceName

    def _set_to_ice(self, dto: "armarx.data.ObjectID"):
        dto.dataset = self.dataset
        dto.className = self.class_name
        dto.instanceName = self.instance_name

    def __repr__(self) -> str:
        return "<{} dataset='{}' class_name='{}' instance_name='{}'>".format(
            self.__class__.__name__, self.dataset, self.class_name, self.instance_name
        )

    def __str__(self) -> str:
        items = [self.dataset, self.class_name]
        if self.instance_name:
            items.append(self.instance_name)
        return self.SEP.join(items)
