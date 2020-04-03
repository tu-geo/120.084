import math
from prg1.utils.angle_operation import great_circle


class FoldingSquare(object):

    def __init__(self, *args, **kwargs):
        self.azimuth = kwargs.get("azimuth", 0.0)
        self.elevation = kwargs.get("elevation", 0.0)
        self.distance = kwargs.get("distance", 0.0)

    def get_chord_from_values(self, azimuth, elevation):
        """
        """
        return great_circle(
            lon_a=self.azimuth, lat_a=self.elevation,
            lon_b=azimuth, lat_b=elevation
        )

    def __sub__(self, other):
        """
        self - other
        """
        return FoldingSquare(
            azimuth=self.azimuth - other.azimuth,
            elevation=self.elevation - other.elevation,
            distance=self.distance - other.distance
        )

    def __add__(self, other):
        """
        self + other
        """
        return FoldingSquare(
            azimuth=self.azimuth + other.azimuth,
            elevation=self.elevation + other.elevation,
            distance=self.distance + other.distance
        )

    def get_chord_from_object(self, other):
        return self.get_chord_from_values(
            other.azimuth, other.elevation
        )

    def __str__(self):
        return "FoldingSquare(azimuth={:11.6f}, elevation={:11.6f}, distance={:15.3f})".format(
            math.degrees(self.azimuth),
            math.degrees(self.elevation),
            1000*self.distance
        )
