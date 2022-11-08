from datetime import datetime

import numpy as np

from armarx import VariantBase
from armarx import TimedVariantBase

from armarx import StringVariantData
from armarx import FloatVariantData
from armarx import BoolVariantData
from armarx import IntVariantData


def hash_type_name(type_id: str) -> int:
    """
    converts an ice id to a variant's type id

    ..see:: c++ implementation in ArmarXCore/observers/variants/Variants.cpp::hashTypeName()

    The implementation uses a normal int, thus the value can be larger than 2 ** 31 - 1

    :param type_id:: the type id
    :returns: the hash value of type_id
    """
    prev_error_level = np.geterr()
    np.seterr(over="ignore")
    hash_value = np.int32(0)
    for ch in type_id:
        hash_value = (
            (np.int32(hash_value) << np.int32(5)) + np.int32(hash_value)
        ) ^ np.int32(ord(ch))
    np.seterr(over=prev_error_level["over"])
    return hash_value


def convert_to_variant_data(data):
    """
    Wraps python data into an ArmarX variant
    """
    if isinstance(data, str):
        return StringVariantData(data)
    elif isinstance(data, float):
        return FloatVariantData(data)
    elif isinstance(data, bool):
        return BoolVariantData(data)
    elif isinstance(data, int):
        return IntVariantData(data)
    return data


class TimedVariant(TimedVariantBase):
    def __init__(self, data=None, _typeId=-1, _timestamp=0):
        super().__init__(data, _typeId=-1, _timestamp=0)
        if self._typeId == -1 and hasattr(data, "ice_id"):
            self._typeId = hash_type_name(self.data.ice_id())
        if _timestamp == 0:
            self._timestamp = datetime.now().timestamp()


class Variant(VariantBase):
    def __init__(self, data=None, _typeId=-1):
        super().__init__(data, _typeId)
        if self._typeId == -1 and hasattr(data, "ice_id"):
            self._typeId = hash_type_name(self.data.ice_id())
