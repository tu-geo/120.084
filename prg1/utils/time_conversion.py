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


def calculate_theta(ti):
    """
    Calculate the rotationen dependet shift for a longitude
    returns additional angle in degree
    """
    t = datetime.datetime(2000, 1, 1).replace(tzinfo=datetime.timezone.utc)
    dt = (ti - t).total_seconds()
    theta = 100.460618375 + 36000.770053608336 * dt + 0.0003879333 * math.pow(dt, 2) + \
        15.0 * ti.hour + ti.minute / 4.0 + ti.second / 240.0
    return theta % 360
    