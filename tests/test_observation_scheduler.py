import unittest
import logging
import math
import datetime

from prg1.models.observation_scheduler import ObservationScheduler, SORT_COL_CHORD, SORT_COL_PRIORITY
from prg1.models.point import GeographicPoint, GeocentricPoint
#from prg1.models.folding_square import FoldingSquare
from prg1.utils.point_conversion import convert_cartesian_to_ellipsoidal


logger = logging.getLogger(__name__)


class ObservationSchedulerTestCase(unittest.TestCase):

    def setUp(self):
        station_geocentric = GeocentricPoint(x=1130745.549, y=-4831368.033, z=3994077.168)
        station_geographic = convert_cartesian_to_ellipsoidal(station_geocentric)

        self.scheduler = ObservationScheduler(
            station_name="Greenbelt",
            # duration=200,
            sort_col=SORT_COL_PRIORITY,
            # skip_known=1,
            station_location=station_geographic,
            station_folding_elevation=math.radians(0.0),
            station_folding_azimuth=math.radians(0.0),
            t_start=datetime.datetime(2020, 3, 28, 0, 0)
        )

    def test_execution(self):
        # return
        self.scheduler.execute()
        self.assertTrue(False)
