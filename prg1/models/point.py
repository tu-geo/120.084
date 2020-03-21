import math


class GeocentricPoint(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def __sub__(self, other):
        assert isinstance(other, GeocentricPoint)
        return GeocentricPoint(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        assert isinstance(other, GeocentricPoint)
        return GeocentricPoint(self.x + other.x, self.y + other.y, self.z + other.z)
        
    def get_norm(self):
        return math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2) + math.pow(self.z, 2))
        
    def __str__(self):
        return "GeocentricPoint(x={:.4f}, y={:.4f}, z={:.4f})".format(self.x, self.y, self.z)
        

class GeographicPoint(object):
    def __init__(self, lon, lat, ele=0.0):
        self.lon = lon
        self.lat = lat
        self.ele = ele

    def __sub__(self, other):
        assert isinstance(other, GeographicPoint)
        return GeographicPoint(self.lon - other.lon, self.lat - other.lat, self.ele - other.ele)

    def __add__(self, other):
        assert isinstance(other, GeographicPoint)
        return GeographicPoint(self.lon + other.lon, self.lat + other.lat, self.ele - other.ele)

    def __str__(self):
        return "GeographicPoint(lon={:.8f}, lat={:.8f}, ele={:.4f})".format(self.lon, self.lat, self.ele)
        