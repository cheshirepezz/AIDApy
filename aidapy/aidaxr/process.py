""" Xarray Accessor that is responsible for conversions """
import math

import numpy as np
import xarray as xr
import pandas as pd
import astropy.units as u


@xr.register_dataarray_accessor('process')
class AidaProcessAccessor:
    """ This class is responsible for converting
                units to other formats """

    def __init__(self, xarray_obj):

        self._obj = xarray_obj

    """
    def convert(self, dim, new_unit):
       # 
       # Docstring
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
    def elev_angle(self):
        """tofill

        Return
        ------
        data : tofill
            tofill

        """
        data = self._obj

        x = data.data[:, 0]
        y = data.data[:, 1]
        z = data.data[:, 2]
        el_angle = np.arctan2(z, np.sqrt(x ** 2 + y ** 2)) * 180 / np.pi
        index = pd.DatetimeIndex(data.time.data)
        elevation_angle = xr.DataArray(el_angle, coords=[index],
                                       dims=['time'])
        elevation_angle.name = 'Elevation Angle'
        elevation_angle.attrs['Units'] = u.Unit('deg')
        return elevation_angle


@xr.register_dataset_accessor('process')
class AidaStatisticsAccessor:
    """Xarray Dataset accessor responsible for the statistical utilities
    """
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def reindex_ds_timestamps(self, sample_freq=None):
        """tofill

        Return
        ------
        data : tofill
            tofill

        """
        # TODO: add check on the dataset to see if we can use the routine
        data = self._obj
        if not sample_freq:
            time_ind = []
            data_ind = []
            for data_prod in data.indexes:
                if isinstance(data.indexes[data_prod], pd.DatetimeIndex):
                    time_ind.append(len(data.indexes[data_prod]))
                    data_ind.append(data_prod)

            smallest_data_obj = data[data_ind[int(np.argmin(time_ind))]]
            time = smallest_data_obj.rename({smallest_data_obj.name: 'time'})

            for i_time, data_obj in enumerate(data):
                data[data_obj] = data[data_obj].rename(
                    {'time' + str(i_time + 1): 'time'}).reindex(
                    {'time': time}, method='nearest')
                data = data.drop('time' + str(i_time + 1))
        else:
            sample_freq = str(
                1 / sample_freq) + 'S'  # Convert from Hz to Pandas/xarray seconds alias
            for i, j in enumerate(data):
                data[j] = data[j].rename(
                    {'time' + str(i + 1): 'time'}).resample(
                    time=sample_freq).interpolate('linear')
                data[j] = data[j].bfill(
                    'time')  # Fill NaNs due to interpolation
                data[j] = data[j].ffill(
                    'time')  # Fill NaNs due to interpolation
                data = data.drop('time' + str(i + 1))

        return data

    def j_curl(self):
        """tofill

        Return
        ------
        data : tofill
            tofill

        """
        data = self._obj

        b_gse = dict()
        r_gse = dict()
        for ic in np.arange(1, 5):
            b_gse[str(ic)] = data['dc_mag' + str(ic)]
            r_gse[str(ic)] = b_gse[str(ic)].attrs['pos_gse']
            r_gse[str(ic)] = r_gse[str(ic)].interp_like(b_gse[str(ic)])

        j, div_b, div_b_bycurl_b = self.curl_b(
            b_gse['1'].data[:, 0:3], b_gse['2'].data[:, 0:3],
            b_gse['3'].data[:, 0:3], b_gse['4'].data[:, 0:3], r_gse['1'].data,
            r_gse['2'].data, r_gse['3'].data, r_gse['4'].data)

        index = pd.DatetimeIndex(b_gse['1'].time.data)
        j = xr.DataArray(j * 1e9, coords=[index[:-1], ['x', 'y', 'z']],
                         dims=['time', 'j_vec'])
        j = j.reindex({'time': data.time})
        j = j.ffill('time')
        j.name = 'Current Density'
        j.attrs['Units'] = u.Unit('nA.m**-2')
        return j

    @staticmethod
    def curl_b(b1, b2, b3, b4, r1, r2, r3, r4):
        """tofill
        Routine taken from esa.
        https://www.cosmos.esa.int/web/csa/multi-spacecraft

        Parameters
        ----------
        b1 : tofill
            tofill

        b2 : tofill
            tofill

        b3 : tofill
            tofill

        b4 : tofill
            tofill

        r1 : tofill
            tofill

        r2 : tofill
            tofill

        r3 : tofill
            tofill

        r4 : tofill
            tofill

        Return
        ------
        jj : tofill
            tofill

        div_b : tofill
            tofill

        div_b_bycurl_b : tofill
            tofill

        """
        # The Curlometer Function
        def delta(ref, i):
            del_ref_i = i - ref
            return del_ref_i

        km2m = 1e3
        n_t2_t = 1e-9
        mu0 = (4 * math.pi) * 1e-7

        jj = np.zeros((len(b1) - 1, 3))
        div_b = np.zeros(len(b1) - 1)
        div_b_bycurl_b = np.zeros(len(b1) - 1)

        for t in np.arange(len(b1) - 1):
            c1_r = r1[t] * km2m
            c1_b = b1[t] * n_t2_t
            c2_r = r2[t] * km2m
            c2_b = b2[t] * n_t2_t
            c3_r = r3[t] * km2m
            c3_b = b3[t] * n_t2_t
            c4_r = r4[t] * km2m
            c4_b = b4[t] * n_t2_t

            del_b14 = delta(c4_b, c1_b)
            del_b24 = delta(c4_b, c2_b)
            del_b34 = delta(c4_b, c3_b)
            del_r14 = delta(c4_r, c1_r)
            del_r24 = delta(c4_r, c2_r)
            del_r34 = delta(c4_r, c3_r)

            # J

            # Have to 'convert' this to a matrix to be able to get the inverse.
            r = np.array([[np.cross(del_r14, del_r24), np.cross(del_r24,
                                                                del_r34),
                           np.cross(del_r14, del_r34)]])
            r_inv = np.linalg.inv(r)

            # I(average) matrix:
            i_ave = np.array(
                [[np.dot(del_b14, del_r24) - np.dot(del_b24, del_r14)],
                 [np.dot(del_b24, del_r34) - np.dot(del_b34, del_r24)],
                 [np.dot(del_b14, del_r34) - np.dot(del_b34, del_r14)]])

            jj[t] = np.squeeze((r_inv @ i_ave) / mu0)

            # div B
            lhs = np.dot(del_r14, np.cross(del_r24, del_r34))

            rhs = np.dot(del_b14, np.cross(del_r24, del_r34)) + \
                  np.dot(del_b24, np.cross(del_r34, del_r14)) + \
                  np.dot(del_b34, np.cross(del_r14, del_r24))

            div_b[t] = abs(rhs) / abs(lhs)

            # div B / curl B
            curl = jj[t] * mu0
            mag_curl_b = math.sqrt(curl[0] ** 2 + curl[1] ** 2 + curl[2] ** 2)
            div_b_bycurl_b[t] = div_b[t] / mag_curl_b

        return jj, div_b, div_b_bycurl_b

    def plasma_beta(self, probe=1, species='i'):
        """tofill

        Return
        ------
        data : tofill
            tofill

        """
        data = self._obj
        probe = str(probe)

        n = data[species+'_dens'+probe]
        temp = (data[species+'_temppara'+probe] + data[species+'_tempperp'+probe]) /2
        b_tot = data['dc_mag'+probe].data[:, 3]
        beta = 4.03e-11 * n.data * temp.data / (b_tot*1e-5)**2
        index = pd.DatetimeIndex(data.time.data)
        beta = xr.DataArray(beta, coords=[index], dims=['time'])

        if species == 'i':
            beta.name = 'Ion Beta'
        elif species == 'e':
            beta.name = 'Electron Beta'
        else:
            raise NotImplementedError

        beta.attrs['Units'] = u.dimensionless_unscaled
        return beta

