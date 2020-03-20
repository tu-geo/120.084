import datetime
import math


def time_to_frac(time):
    """Calculate daily fractal"""
    assert isinstance(time, datetime.time)
    h = time.hour
    m = time.minute
    s = time.second
    return ((h*60 + m) * 60 + s) / 86400.0


def frac_to_time(frac):
    """Calculate time from daily fractal"""
    t = math.fabs(frac * 86400.0)
    h = t / 3600
    m = (t % 3600) / 60
    s = (m * 60) % 60
    return datetime.time(hour=int(h), minute=int(m), microsecond=int(s*1000))
