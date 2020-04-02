import numpy as np


class Orbit(object):

    def __init__(self, satellite_id, azimuth_list, elevation_list):
        self.__azimuth_list = azimuth_list
        self.__elevation_list = elevation_list
        assert len(self.__azimuth_list) == len(self.__elevation_list)
        self.satellite_id = satellite_id

    def add_folding(self, azimuth: float, elevation: float):
        np.append(self.__azimuth_list, azimuth)
        np.append(self.__elevation_list, elevation)
        return self

    def get_azimuth_array(self):
        return self.__azimuth_list

    def get_azimuth_radian_array(self):
        return np.radians(self.get_azimuth_array())

    def get_elevation_array(self):
        return self.__elevation_list

    def get_elevation_polar_array(self):
        #return self.__elevation_list
        return np.array([90.0 - v for v in self.__elevation_list.tolist()])
