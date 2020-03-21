from prg1.utils.constants import *

oed = OMEGA_E_DOT

class NuisanceParameterSet(object):
    def __init__(self, delta_n=0, omega_dot=oed, i_dot=0, c_us=0, c_uc=0, c_is=0, c_ic=0, c_rs=0, c_rc=0):
        self.delta_n = delta_n
        self.omega_dot = omega_dot
        self.i_dot = i_dot
        self.c_us = c_us
        self.c_uc = c_uc
        self.c_is = c_is
        self.c_ic = c_ic
        self.c_rs = c_rs
        self.c_rc = c_rc
