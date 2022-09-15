import armarx.arviz.load_slice

from armarx.ice_conv.ice_converter import IceConverter
from armarx.math.transform import Transform


class GlobalPoseConv(IceConverter):
    @classmethod
    def _import_dto(cls):
        return armarx.viz.data.GlobalPose

    def _to_ice(self, bo: Transform, *args, **kwargs):
        dto = self.get_dto()()
        dto.x, dto.y, dto.z = bo.translation
        dto.qw, dto.qx, dto.qy, dto.qz = map(float, bo.rot_quat)
        return dto

    def _from_ice(self, dto: armarx.viz.data.GlobalPose, *args, **kwargs):
        return Transform(
            translation=(dto.x, dto.y, dto.z), rotation=(dto.qw, dto.qx, dto.qy, dto.qz)
        )
