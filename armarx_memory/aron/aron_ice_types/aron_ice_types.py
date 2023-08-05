from .import_aron_slice import import_aron_slice

armarx_aron = import_aron_slice()
data_dto = armarx_aron.data.dto


class AronIceTypes:
    ARON_VERSION = armarx_aron.Version()

    Version = armarx_aron.Version

    Data = data_dto.GenericData

    String = data_dto.AronString
    Bool = data_dto.AronBool
    Int = data_dto.AronInt
    Long = data_dto.AronLong
    Float = data_dto.AronFloat
    Double = data_dto.AronDouble

    List = data_dto.List
    Dict = data_dto.Dict

    NDArray = data_dto.NDArray

    @classmethod
    def string(cls, value: str) -> String:
        return cls.String(value=value, VERSION=cls.ARON_VERSION)

    @classmethod
    def bool(cls, value: int) -> Bool:
        return cls.Bool(value=value, VERSION=cls.ARON_VERSION)

    @classmethod
    def int(cls, value: int) -> Int:
        return cls.Int(value=value, VERSION=cls.ARON_VERSION)

    @classmethod
    def long(cls, value: int) -> Long:
        return cls.Long(value=value, VERSION=cls.ARON_VERSION)

    @classmethod
    def float(cls, value: float) -> Float:
        return cls.Float(value=value, VERSION=cls.ARON_VERSION)

    @classmethod
    def double(cls, value: float) -> Double:
        return cls.Double(value=value, VERSION=cls.ARON_VERSION)

    @classmethod
    def list(cls, elements: list) -> List:
        return cls.List(elements=elements, VERSION=cls.ARON_VERSION)

    @classmethod
    def dict(cls, elements: dict) -> Dict:
        return cls.Dict(elements=elements, VERSION=cls.ARON_VERSION)
