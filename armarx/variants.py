from .slice_loader import load_armarx_slice
load_armarx_slice('ArmarXCore', 'observers/ObserverInterface.ice')

from armarx import VariantBase
from armarx import TimedVariantBase

from datetime import datetime


def hash_type_name(type_id):
    """
    converts an ice id to a variant's type id
    ..see:: c++ implementation in ArmarXCore/observers/variants/Variants.cpp::hashTypeName()

    :param type_id:: the type id
    :type type_id:: basestring
    :returns: the hash value of type_id
    :rtype: int
    """
    hash_value = 0
    for ch in type_id:
        hash_value = (((hash_value << 5) + hash_value) & 0xffffffff) ^ ord(ch)
    return hash_value


class TimedVariant(TimedVariantBase):

    def __init__(self, data=None, _typeId=-1, _timestamp=0):
        super().__init__(data, _typeId=-1, _timestamp=0)
        if self._typeId == -1 and hasattr(data, 'ice_id'):
            self._typeId = hash_type_name(self.data.ice_id())
        if _timestamp == 0:
            self._timestamp = datetime.now().timestamp()


class Variant(VariantBase):

    def __init__(self, data=None, _typeId=-1):
        super().__init__(data, _typeId)
        if self._typeId == -1 and hasattr(data, 'ice_id'):
            self._typeId = hash_type_name(self.data.ice_id())
