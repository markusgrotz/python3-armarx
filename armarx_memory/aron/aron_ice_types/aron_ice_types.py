from .import_aron_slice import import_aron_slice

import numpy as np

from armarx_memory.aron.common.time import *
from datetime import datetime

try:
    # beta 0.2.3
    class AronIceTypes:
        ARON_VERSION = "beta 0.2.3"

        ns = import_aron_slice().data.dto

        Data = ns.GenericData

        String = ns.AronString
        Bool = ns.AronBool
        Int = ns.AronInt
        Long = ns.AronLong
        Float = ns.AronFloat

        List = ns.List
        Dict = ns.Dict

        NDArray = ns.NDArray

        @classmethod
        def datetime(cls, value: datetime) -> Dict:
            ret = DateTime()
            ret.clockType = int(ClockTypeEnum.Realtime) # TODO FIX ME!
            ret.hostname = "localhost"
            ret.timeSinceEpoch.microSeconds = np.int64(value.timestamp() * 1e6)

            return ret.to_aron_ice()

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
        def list(cls, elements: list) -> List:
            return cls.List(elements=elements, VERSION=cls.ARON_VERSION)

        @classmethod
        def dict(cls, elements: dict) -> Dict:
            return cls.Dict(elements=elements, VERSION=cls.ARON_VERSION)

except AttributeError as e:
    # < 0.2.3

    class AronIceTypes:

        ns = import_aron_slice().data

        Data = ns.AronData

        String = ns.AronString
        Bool = ns.AronBool
        Int = ns.AronInt
        Long = ns.AronLong
        Float = ns.AronFloat

        List = ns.AronList
        Dict = ns.AronDict

        NdArray = ns.AronNDArray
