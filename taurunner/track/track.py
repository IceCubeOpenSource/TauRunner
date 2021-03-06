import numpy as np
import warnings
from scipy.integrate import quad
from scipy.interpolate import splrep, splev, interp1d
from taurunner.modules import units

class Track(object):

    def __init__(self, depth=0.0):
        self.depth                   = depth
        self._column_depth_functions = {}
      
    def _column_depth(self, body, xi, xf, safe_mode=True):
        '''
        params
        ______
        body (Body)  : TauRunner Body object for which you want the column depth
        xi   (float) : Affine track parameter at which to start the integeration.
        xf   (float) : Affine track parameter at which to end the integeration.

        returns
        _______
        column_depth (float) : column depth on the portion of the track from xi to xf [natural units]
        '''
        if not (xi<=xf):
            raise RuntimeError('xi must be less than or equal to xf')
        integrand = lambda x: body.get_density(self.x_to_r(x))*self.x_to_d_prime(x)*body.radius
        # find where the path intersects layer boundaries
        xx        = []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for r in body.layer_boundaries:
                xx = np.append(xx, self.r_to_x(r))
        # NaNs means it does not intersect the layer
        xx        = xx[np.where(~np.isnan(xx))[0]] # non-nanize
        # Remove xs before and after the integration limits
        mask      = np.where(np.logical_and(xi<xx, xx<xf))[0]
        xx        = np.hstack([[xi], xx[mask], [xf]])
        II        = []
        for xi, xf in zip(xx[:-1], xx[1:]):
            I = quad(integrand, xi, xf)
            if safe_mode:
                if I[0]!=0:
                    if I[1]/I[0]>1e-3:
                        raise RuntimeError('Error too large')
            II.append(I[0])
        return np.sum(II)

    def d_to_x(self, d) :
        '''
        Convert from distance traveled to track parameter

        params
        ______
        d (float) Distance traveled along the track in units of radius of the body.
    
        returns
        _______
        x (float): Affine parameter between 0 and 1 which parametrizes the track
        '''
        pass 

    def _initialize_column_depth_functions(self, body):
        xx            = np.linspace(0, 1, 101)
        column_depths = np.append(0, np.cumsum([self._column_depth(body, x[0], x[1]) for x in zip(xx[:-1], xx[1:])]))
        # Pad arrays to help spliine stability
        npad          = 5
        xpad          = np.linspace(0.01, 0.05, npad)
        padded_xx     = np.hstack([-xpad[::-1], xx, 1+xpad])
        padded_cds    = np.hstack([np.full(npad, column_depths[0]), column_depths, np.full(npad, column_depths[-1])])
        #x_to_X        = interp1d(xx, column_depths, kind='linear', bounds_error=False, fill_value=(np.min(column_depths), np.max(column_depths)))
        #X_to_x        = interp1d(column_depths, xx, kind='linear', bounds_error=False, fill_value=(np.min(xx), np.max(xx)))
        x_to_X_tck    = splrep(padded_xx, padded_cds)
        X_to_x_tck    = splrep(column_depths, xx)
        x_to_X        = lambda x: splev(x, x_to_X_tck)
        X_to_x        = lambda X: splev(X, X_to_x_tck)
        
        self._column_depth_functions[body._name] = (column_depths[-1], x_to_X, X_to_x)
        


    def r_to_x(self, r):
        '''
        Convert from radius to track parameter

        params
        ______
        r (float) Radius. Must be between 0 and 1.
    
        returns
        _______
        x (float): Affine parameter between 0 and 1 which parametrizes the track
        '''
        pass

    def total_column_depth(self, body, safe_mode=True):
        '''
        params
        ______
        body (Body) : TauRunner Body object for which you want the column depth

        returns
        _______
        column_depth (float) : total column depth for the entire track [natural units]
        '''
        if body._name not in self._column_depth_functions.keys():
            self._initialize_column_depth_functions(body)
        return self._column_depth_functions[body._name][0]

    def x_to_cartesian_direction(x):
        '''
        Convert from track parameter to direction in cartesian space

        params
        ______
        x (float): Affine parameter between 0 and 1 which parametrizes the track

        returns
        _______
        cart_dir (tuple): x-, y-, and z-directions in a cartesian system whose origin coincides
                          with the center of the body

        '''
        pass

    def x_to_d(self, x):
        '''
        Convert from track parameter to distance traveled

        params
        ______
        x (float): Affine parameter between 0 and 1 which parametrizes the track
    
        returns
        _______
        d (float) Distance traveled along the track in units of radius of the body.
        '''
        pass

    def x_to_d_prime(self, x):
        '''
        Derivative of self.x_to_d with respect to the affine track parameter

        params
        ______
        x (float): Affine parameter between 0 and 1 which parametrizes the track
    
        returns
        _______
        dd/dx (float) Derivative of self.x_to_r with respect to the affine track parameter
        '''
        pass

    def x_to_r(self, x):
        '''
        Convert from radius to track parameter

        params
        ______
        x (float): Affine parameter between 0 and 1 which parametrizes the track
    
        returns
        _______
        r (float) Radius. Must be between 0 and 1.
        '''
        pass

    def X_to_x(self, body, X):
        '''
        Returns the affine track parameter at which the track has traversed a given column depth
        in a given body. If column depth is greater than the total column depth it raises an error
        
        params
        ______
        body (Body) : TauRunner body object
        X    (float): Column depth [natural units]

        returns
        _______
        x (float): Affine track parameter
        '''
        if body._name not in self._column_depth_functions.keys():
            self._initialize_column_depth_functions(body)
            print('should only print once')
        max_X = self._column_depth_functions[body._name][0]
        if X<=max_X:
            return self._column_depth_functions[body._name][2](X)
        else:
            raise ValueError('Column depth was greater than total')

    def x_to_X(self, body, x):
        if body._name not in self._column_depth_functions.keys():
            print('should only print once')
            self._initialize_column_depth_functions(body)
        return self._column_depth_functions[body._name][1](x)
