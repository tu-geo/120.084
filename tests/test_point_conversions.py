import unittest
import math
import logging

from prg1.models.point import GeocentricPoint, GeographicPoint
from prg1.utils.point_conversion import convert_ellipsoidal_to_cartesian, \
    convert_cartesian_to_ellipsoidal, ELLIPSOID_AXIS_MAJOR, ELLIPSOID_FLATTENING, \
    get_azimuth_and_elevation


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class OrbitalTestCase(unittest.TestCase):
    
    def setUp(self):
        self.point_cartesian = GeocentricPoint(4134646.623794, 1180600.051953, 4696218.309687)
        self.point_ellipsoidal = GeographicPoint(15.936074303, 47.7141083, 906.843)
        self.ellipsoid_major_axis = ELLIPSOID_AXIS_MAJOR
        self.ellipsoid_flattening = ELLIPSOID_FLATTENING

    def test_cartesian_to_ellipsoidal(self):
        point_ellipsoidal = convert_cartesian_to_ellipsoidal(
            axis_major=self.ellipsoid_major_axis,
            flattening=self.ellipsoid_flattening,
            src_point=self.point_cartesian
        )            
        self.assertAlmostEqual(point_ellipsoidal.ele, self.point_ellipsoidal.ele, places=4)
        self.assertAlmostEqual(point_ellipsoidal.lon, self.point_ellipsoidal.lon, places=9)
        self.assertAlmostEqual(point_ellipsoidal.lat, self.point_ellipsoidal.lat, places=9)

    def test_ellipsoidal_to_cartesian(self):
        point_cartesian = convert_ellipsoidal_to_cartesian(
            axis_major=self.ellipsoid_major_axis, 
            flattening=self.ellipsoid_flattening, 
            src_point=self.point_ellipsoidal)
        self.assertAlmostEqual(point_cartesian.x, self.point_cartesian.x, places=4)
        self.assertAlmostEqual(point_cartesian.y, self.point_cartesian.y, places=4)
        self.assertAlmostEqual(point_cartesian.z, self.point_cartesian.z, places=4)

    def test_local_enu(self):
        station = GeographicPoint(12.879958, 47.7309909, 500.0)
        satellite = GeographicPoint(19.2, 0.0, 2000e3)
        #enu = to_local_enu(station, satellite)
        a, e = get_azimuth_and_elevation(station, satellite)
        print(a, e)
        self.assertTrue(False)
