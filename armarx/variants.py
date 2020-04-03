from .slice_loader import load_armarx_slice
load_armarx_slice('ArmarXCore', 'observers/ObserverInterface.ice')

from armarx import VariantBase
from armarx import TimedVariantBase

from datetime import datetime
import numpy as np


def hash_type_name(type_id):
    """
    converts an ice id to a variant's type id

    ..see:: c++ implementation in ArmarXCore/observers/variants/Variants.cpp::hashTypeName()

    The implementation uses a normal int, thus the value can be larger than 2 ** 31 - 1 

    :param type_id:: the type id
    :type type_id:: basestring
    :returns: the hash value of type_id
    :rtype: int
    """
    prev_error_level = np.geterr()
    np.seterr(over='ignore')
    hash_value = np.int32(0)
    for ch in type_id:
        hash_value = ((np.int32(hash_value) << np.int32(5)) + np.int32(hash_value)) ^ np.int32(ord(ch))
    np.seterr(over=prev_error_level['ignore'])
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
