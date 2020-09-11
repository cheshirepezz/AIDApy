"""AIDA module responsible for the statistical utilities of the timeseries
"""
from collections import OrderedDict
import numpy as np
import xarray as xr


@xr.register_dataarray_accessor('statistics')
class AidaAccessorStatistics:
    """Xarray accessor responsible for the statistical utilities
    """
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def sfunc(self, scale=[1], order=2):
        """
        Returns the structure function of a timeseries

        .. math::

           y= \\frac{1}{N-s}\\sum_{i=1}^{N-s}(x_i - x_{i+s})^o

        where :math:`s` is the scale, and :math:`o` is the order.

        Parameters
        ----------
        scale : `list` or `numpy.array`
            A list or an array containing the scales to calculate.

        order : `int`
            Order of the exponential of the structure function.

        Returns
        -------
        values : `~xarray.DataArray`
            An xarray containing the structure functions, one per
            product in the original timeseries. The index coordinate
            contains the scale value, and the attribute 'order' keeps
            a record on the order used for its calculation.

        """
        data = self._obj.values
        if len(data.shape) == 1:
            data = data.reshape((-1, 1))
        result = []
        for s in scale:
            f = np.mean(np.abs((data[s:, :]-data[:-s, :])**order), axis=0)
            result.append(f)
        result = np.array(result)

        c = self._obj.dims[1]
        cols = self._obj.coords[c]
        result = xr.DataArray(result,
                              coords=[scale, cols],
                              dims=['scale', c],
                              attrs=self._obj.attrs)
        result.attrs['order'] = order
        return result

    def mean(self, **kwargs):
        """
        Calculates the mean of on xarray DataArray

        Parameters
        ----------
        coord : `int`
            The keyword is the coordinate of the xarray on which the
            mean will be calculated. The value given is the size of
            the sliding window.

        center : `bool`
            If true the resulting value will be placed in the middle
            index of the window, otherwise it will be placed in the
            last index of the window.

        Returns
        -------
        values : `~xarray.DataArray`
            An xarray containing the values of the mean in the
            requested coordinate.

        """
        result = self._obj.rolling(**kwargs).mean()
        return result

    def std(self, **kwargs):
        """
        Calculates the standar deviation of on xarray DataArray

        Parameters
        ----------
        coord : `int`
            The keyword is the coordinate of the xarray on which the
            std will be calculated. The value given is the size of
            the sliding window.

        center : `bool`
            If true the resulting value will be placed in the middle
            index of the window, otherwise it will be placed in the
            last index of the window.

        Returns
        -------
        values : `~xarray.DataArray`
            An xarray containing the values of the std in the
            requested coordinate.
        """
        result = self._obj.rolling(**kwargs).std()
        return result

    def psd(self, timeu='s', **kwargs):
        """
        Calculates the power specral density using the signal.welch
        routine from scipy

        Parameters
        ----------
        timeu : `str`
            Sampling unit of the signal. Default is 's'
        **kwargs :
            arguments used by the signal.welch method of
            scipy

        Returns
        -------
        values : `~xarray.DataArray`
            An xarray containing the values of the PSD, were the
            index is the frequency and the units are in Hz
        """
        from scipy import signal

        data = self._obj.values
        freq, psd = signal.welch(data, axis=0, **kwargs)

        c = self._obj.dims[1]
        cols = self._obj.coords[c]
        result = xr.DataArray(psd,
                              coords=[freq, cols],
                              dims=['frequency', c],
                              attrs=self._obj.attrs)
        result.attrs['units'] = 'Hz'

        return result

    def autocorr(self, lagbeg=0, stride=1, dt=1, timeu='s', normalize=True):
        """
        Calculates the autocorrelation of the xarray per column.

        Parameters
        ----------
        lagbeg : `int`
            Default = 0. Initial lag.
        stride : `int`
            Default = 1. Stride of the window to autocorrelate.
        dt : `int`
            Default = 1. Sampling frequeny of the signal.
        timeu : `str`
            Default = 's'. Time unit of the signal.
        normalize : `bool`
            Default = True. Normalizes the autocorrelation

        Returns
        -------
        values : `~xarray.DataArray`
            An xarray containing the values of the autocorrelation,
            where the index is the lag and the units are the same as
            the input vector
        """

        x = self._obj.values[lagbeg::stride]
        y = [np.correlate(x[:,i], x[:,i], 'full') for i in range(x.shape[1])]
        y = np.array(y).T
        if normalize:
            y = y / np.abs(y.max(axis=0))
        y = y[y.shape[0]//2:]

        dt = np.timedelta64(dt, timeu)
        fs = 1.0 / (dt / np.timedelta64(1, timeu))
        lag = lagbeg + stride*fs * np.arange(len(y))
        c = self._obj.dims[1]
        cols = self._obj.coords[c]
        result = xr.DataArray(y,
                              coords=[lag, cols],
                              dims=['lag', c],
                              attrs=self._obj.attrs)
        result.attrs['units'] = timeu

        return result

    def psdwt(self, *args):
        """
        Returns the wavelet transform of a timeseries

        Parameters
        ----------
        *args :
        Arguments used in scipy.signal.cwt

        Returns
        -------
        values : `~xarray.DataArray`
            An xarray containing the wavelet transform of the original timeseries.
            The signal has to be one dimensional. The name of the first dimension
            is used as first dimension in the resulting xarray.

        """
        from scipy import signal
        assert(len(self._obj.dims)==1)

        x = self._obj.values
        i = self._obj.dims[0]
        t = self._obj.coords[i]

        cwtmatr = signal.cwt(x, *args).T
        widths = np.arange(1,cwtmatr.shape[1]+1)

        result = xr.DataArray(cwtmatr,
                              coords = [t, widths],
                              dims=[i,'scale'],
                              attrs=self._obj.attrs)
        result.attrs['units'] = 'Amplitude'
        ## Should we return this as attribute?:
        #en=np.abs(wave)**2
        #sp=2*dt*np.sum(en)/nn
        #return sp
        return result

@xr.register_dataset_accessor('statistics')
class AidaStatisticsAccessor:
    """Xarray Dataset accessor responsible for the statistical utilities
    """
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def _check_var(self, var):
        if isinstance(var, str):
            varss = set([var])
        elif isinstance(var, str):
            if not all(isinstance(v, str) for v in var):
                raise ValueError('The list of variables {} must be a list of string'.format(var))
            varss = set(var)
        elif var is None:
            varss = set(self._obj.data_vars)

        missing_vars = [v for v in varss if v not in self._obj.data_vars]
        if missing_vars:
            raise ValueError('Dataset does not contain the data variable: %s'
                             % missing_vars)
        return varss

    def _check_dim(self, dim):
        if isinstance(dim, str):
            dims = set([dim])
        elif isinstance(dim, str):
            if not all(isinstance(s, str) for s in dim):
                raise ValueError('The list of dimension {} must be a list of string'.format(dim))

            dims = set(dim)
        elif dim is None:
            dims = set(self._obj.dims)

        missing_dimensions = [d for d in dims if d not in self._obj.dims]
        if missing_dimensions:
            raise ValueError('Dataset does not contain the dimensions: %s'
                             % missing_dimensions)
        return dims

    def _generalize_to_dataset(self, func, var, dim, **kwargs):
        varss = self._check_var(var)
        dims = self._check_dim(dim) #Unused variable
        processed_array = OrderedDict()
        for name_array, data_array in self._obj.data_vars.items():
            if name_array in varss:
                to_add = getattr(data_array.statistics, func)(**kwargs)
                processed_array[name_array] = to_add
        return processed_array

    def sfunc(self, var=None, dim=None, scale=[1], order=2):
        """
        Generalizes the sfunc to xr.Dataset
        """
        return self._generalize_to_dataset('sfunc', var, dim, scale=scale, order=order)


"""
@xr.register_dataarray_accessor('process')
class AidaAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def convert(self, dim, new_unit):
        ##
        #Docstring
        #
        current_unit = self._obj.attrs[]


    def __call__(self, new_unit):
        if self._unit is None:
            raise ValueError("No valid units for field")
        new_unit = astropy.units.Unit(new_unit)
        factor = self._unit.to(new_unit)
        newval = self._obj*factor
        newval.attrs = self._obj.attrs.copy()
        newval.attrs['units'] = new_unit.name
        return newval
"""
