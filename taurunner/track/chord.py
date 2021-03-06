import numpy as np
import sys

from .track import Track
from taurunner.modules import doc_inherit

class Chord(Track):

    def __init__(self, depth=0.0, theta=0.0):
        Track.__init__(self, depth=depth)
        self.theta = theta
        self._c    = np.cos(theta)
        self._s    = np.sin(theta)
        self._m    = np.cos(theta) + np.sqrt((1-depth)**2-np.sin(theta)**2)

    def __str__(self):
        desc = (self.theta, self._m)
        return 'theta = %f radians\nm     = %f' % desc

    @doc_inherit
    def d_to_x(self, d):
        return d/self._m

    @doc_inherit
    def x_to_d_prime(self, x):
        return self._m

    @doc_inherit
    def x_to_d(self, x):
        return self._m*x

    @doc_inherit
    def x_to_cartesian_direction(x):
        direction = np.array(-self._s, 0., self._c+(1-self.depth))
        direction /= np.norm(direction)
        return tuple(direction)

    @doc_inherit
    def r_to_x(self, r):
        val1 = (self._c - np.sqrt(r**2- self._s**2))/self._m
        val2 = (self._c + np.sqrt(r**2- self._s**2))/self._m
        if val1!=val2:
            return (val1, val2)
        else:
            return val1

    @doc_inherit
    def x_to_r(self, x):
        return np.sqrt(self._s**2 + (self._c-self._m*x)**2)
    
    @doc_inherit
    def x_to_r_prime(self, x):
        return np.abs(self._c-self._m*x)*(-self._m)/self.x_to_r(x)
