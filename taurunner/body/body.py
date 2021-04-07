import numpy as np
import sys
from taurunner.modules import units, Callable


class Body(object):

    def __init__(self, density, radius, layer_boundaries=None, name=None):
        r'''
        params
        ______
        density (something) :
        radius (float) : Radius of the body [meters]

        '''

        self.radius = radius*units.km
        self._name  = name
        # Check if body is segmented
        if hasattr(density, '__iter__'):
            if layer_boundaries is None:
                raise RuntimeError('You must specify layer boundaries')
            elif len(layer_boundaries)!=len(density)+1:
                raise RuntimeError('Density and layer_boundaries must have same length.')
            else:
                self._is_layered      = True
                self._density         = [units.gr/units.cm**3*Callable(obj) for obj in density]
                self.layer_boundaries = layer_boundaries
        else:
            self._is_layered      = False
            self._density         = [units.gr/units.cm**3*Callable(density)]
            self.layer_boundaries = np.array([0.0, 1.0])

    def get_density(self, r):
        if r==1:
            layer_index = -1
        else:
            layer_index = np.digitize(r, self.layer_boundaries)-1
        current_density = self._density[layer_index]
        return current_density(r)
