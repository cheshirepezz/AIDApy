"""AIDA module responsible for the Graphical utilities of the timeseries
Contributors: Etienne Behar
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr


@xr.register_dataset_accessor('graphical')
@xr.register_dataarray_accessor('graphical')
class AidaAccessorGraphical:
    """Xarray accessor responsible for the Graphical utilities
    """
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def peek(self):
        """
        Plot of the time series

        Parameters
        ----------
        axes : `~matplotlib.axes.Axes` or None
            If provided the image will be plotted on the given axes. Otherwise
            the current axes will be used.

        **plot_args : `dict`
            Any additional plot arguments that should be used
            when plotting.
        """
        def xr_find_time_index(xarr):
            name = None
            for index in xarr.dims:
                if xarr.coords[index].values.dtype == np.dtype('datetime64[ns]'):
                    name = index
            if name:
                return name
            else:
                raise TimeIndexNotFound

        def _find_proper_coord(indexes, __tindex):
            for ind in indexes:
                if ind == __tindex:
                    continue
                return ind

        def _proper_plot(_data, _tindex):
            indexes = [key for key in _data.dims]
            _var = _find_proper_coord(indexes, _tindex)
            names = _data.coords[_var].values
            values = _data.coords[_tindex].values
            for ik, nam in enumerate(names):
                plt.plot(values, _data.values[:, ik], c=np.random.rand(3, ),
                         label=nam, markersize=14)

        if isinstance(self._obj, xr.Dataset):
            cols = self.find_columns_name()
            for _, var in enumerate(cols):
                data = self._obj[var]
                if len(data.values.shape) == 2:
                    time_index = xr_find_time_index(data)
                    _proper_plot(data, time_index) # TODO: Adapt the labels for multiple probes
                else:
                    data.plot(c=np.random.rand(3, ),
                              label=data.name, markersize=14) # TODO: Remove random colors

        elif isinstance(self._obj, xr.DataArray):
            if len(self._obj.values.shape) == 2:
                time_index = self.find_time_index()
                _proper_plot(self._obj, time_index)
            else:
                self._obj.plot(c=np.random.rand(3, ), label=self._obj.name,
                               markersize=14) # TODO: Remove random colors
        else:
            raise ValueError

        #pylab.legend(loc='upper left')
        plt.show()

    def find_columns_name(self):
        """
        Method to automatically find the name of the columns of the xarray

        Returns
        -------
        col : list
            the name of the columns of the xarray

        """
        col = list()
        if isinstance(self._obj, xr.Dataset):
            for key in self._obj.data_vars:
                col.append(key)
        elif isinstance(self._obj, xr.DataArray):
            for dim in self._obj.dims:
                col.append(dim)
        else:
            raise ValueError
        return col

    def find_time_index(self):
        """
        Method to automatically find the time index of xarray

        Returns
        -------
        name : str
            the name of the time index

        """
        name = None
        for index in self.index_names():
            if self._obj.coords[index].values.dtype == np.dtype('datetime64[ns]'):
                name = index
        if name:
            return name
        else:
            raise TimeIndexNotFound

    def index_names(self):
        """
        The data indexes names
        """
        keys = list()
        for key in self._obj.dims:
            keys.append(key)
        return keys

class TimeIndexNotFound:
    """Error Class responsible for the time index"""
