"""AIDA module responsible for the vdf handling.
etienne.behar
"""
import sys
import time
from datetime import timedelta
import matplotlib as mpl
import numpy as np
from matplotlib.dates import date2num
import xarray as xr
from scipy.interpolate import RegularGridInterpolator
import scipy.stats
from scipy.interpolate import interp1d
from scipy.spatial.transform import Rotation as R
try:
    import tricubic
    tricubic_imported = True
except ModuleNotFoundError:
    tricubic_imported = False
import aidapy.tools.vdf_plot as vplt
import aidapy.tools.vdf_utils as vdfu

@xr.register_dataset_accessor('vdf')
class AidaAccessorVDF:
    """
    Xarray accessor responsible for the vdf utilities.
    """
    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self.settings = xarray_obj.attrs['load_settings']
        self.R_eci_to_gse = None
        self.R_gse_to_eci = None
        self.R_eci_to_gse = None
        self.R_gse_to_eci = None
        self.R_eci_to_dbcs = None

    def interpolate(self, start_time, end_time, start_time_sub,
                    end_time_sub, species, frame, grid_geom,
                    v_max, resolution='60', interp_schem='near', verbose=True):
        """
        Main method of the AidaAccessorVDF.

        Pre-processes the loaded data, initialises the rotation matrices and
        translations vectors, selects a time sub-interval, interpolates the
        data, post-process them and save them as new variables of the
        xarray dataset.
        """
        vdf0, time_par, speed, theta, phi,\
        nb_vdf, B_gse_par = self._preprocess_data(species)
        self._check_inputs(time_par, start_time, end_time,
                          start_time_sub, end_time_sub, grid_geom)
        self._init_rotations_matrices(time_par, start_time, end_time)
        R_b_to_dbcs, R_dbcs_to_b = self._init_R_b_to_dbcs(time_par, B_gse_par)
        ibulkv_dbcs_par = self._init_ibulkv(species, time_par)
        ind_dis_oi, ind_start, ind_stop = self._time_sub_range(nb_vdf, time_par,
                                                              start_time_sub,
                                                              end_time_sub)

        if verbose:
            self._verbosity(grid_geom, resolution, interp_schem,
                           time_par, ind_dis_oi, ind_start, ind_stop)

        grid_cart, grid_spher, grid_cyl, dvvv = \
        vdfu.init_grid(v_max, resolution, grid_geom)
        # vdf_interp will contain the interpolated, averaged, values,
        #    along time and the 3 velocity dimensions.
        vdf_interp = np.zeros((resolution, resolution, resolution))
        vdf_scaled = np.zeros((resolution, resolution, resolution))
        vdf_normed = np.zeros((resolution, resolution, resolution))
        vdf_interp_time = np.zeros((ind_dis_oi.size, resolution, resolution),
                                   dtype=np.float32)
        vdf_scaled_time = np.zeros((ind_dis_oi.size, resolution, resolution),
                                   dtype=np.float32)
        vdf_normed_time = np.zeros((ind_dis_oi.size, resolution, resolution),
                                   dtype=np.float32)
        time_interp = time_par[ind_dis_oi]
        #_________
        nb_dis_final = 0
        nb_pix_final = np.zeros_like(vdf_interp)
        # Re-cacluclating moments based on the integrated interpolated VDF values.
        ne = np.zeros(nb_vdf)
        ve = np.zeros((nb_vdf, 3))
        # From here, whatever coordinate system we chose is of no importance, as each
        #    node of the grid-of-interest will be considered separately.
        tic = time.time()
        # Loop over the scans, since I couldn't find a way to vectorize
        #     the np.dot() method, or the interpolations.
        for i, iS in enumerate(ind_dis_oi):
            if (iS % 10 == 0)*verbose:
                print('{}/{} (current VDF/nb total VDFs)'.format(iS, nb_vdf), end='\r')

            grid_s = self._transform_grid(grid_cart, R_b_to_dbcs[iS],
                                         ibulkv_dbcs_par[:, iS], frame)
            d = self._interpolate_spher_mms(vdf0[iS], speed, theta, phi,
                                           grid_s, interp_schem)
            #
            nb_dis_final += 1
            nb_pix_final += (~np.isnan(d))
            d[np.isnan(d)] = 0.
            if np.nanmax(d) == 0.:
                print(iS, 'np.nanmax(d) == 0. Either empty data'
                          ' or grid-of-interest wrongly set.')
            # Integrated moments.
            ne[nb_dis_final-1] = np.nansum(dvvv * d)
            ve[nb_dis_final-1] = np.nansum(grid_cart * d * dvvv, axis=(1, 2, 3))\
                                           / ne[nb_dis_final-1]
            # Original VDF.
            vdf_interp += d
            if grid_geom == 'spher':
                vdf_interp_time[i] = np.nanmean(d, axis=2)
                # 0-to-1 scaling
                ds = d - np.nanmin(d, axis=(1, 2))[:, None, None]
                ds /= np.nanmax(ds, axis=(1, 2))[:, None, None]
                vdf_scaled_time[i] = np.nanmean(ds, axis=2)
                # Normalisation
                ind_mid = int(resolution/2.)
                wid = int(5.*resolution/180.)
                dn = d/np.nanmean(d[:, ind_mid-wid: ind_mid+wid], axis=(1, 2))[:, None, None]
                vdf_normed_time[i] = np.nanmean(dn, axis=2)
            elif grid_geom == 'cyl':
                vdf_interp_time[i] = np.nanmean(d, axis=1)
            elif grid_geom == 'cart':
                # This is far from ideal, we drop one dimension for saving memory.
                #    If it is acceptable in spherical to average over the gyro-angle
                #    it is not satisfying in this cartesian case. At least, we drop v_y
                #    and save v_z=v_para.
                vdf_interp_time[i] = np.nanmean(d, axis=1)

        if verbose:
            print('')
            print('Total runtime: {} s.\n'.format(int(time.time()-tic)))
        # For now vdf_interp contains the sum all distributions. We need to smartly
        #    average these values, without dividing by zeros. We use a threshold
        #    on the minimum amount of valid vdf values per grid node: nb_pix_min.
        nb_pix_min = min(len(ind_dis_oi)-1, 100)
        itk = (nb_pix_final > nb_pix_min)
        vdf_interp[itk] /= nb_pix_final[itk]
        vdf_interp[~itk] = 0.
        #
        if grid_geom == 'spher':
            vdf_scaled = vdf_interp - np.nanmin(vdf_interp, axis=(1, 2))[:, None, None]
            vdf_scaled /= np.nanmax(vdf_scaled, axis=(1, 2))[:, None, None]
            ind_mid = int(resolution/2.)
            wid = int(5.*resolution/180.)
            vdf_normed = vdf_interp.copy()
            vdf_normed /= np.nanmean(vdf_normed[:, ind_mid-wid: ind_mid+wid],
                                     axis=(1, 2))[:, None, None]

        self._save_xarray_variables(vdf_interp, vdf_scaled, vdf_normed,
                                   vdf_interp_time, vdf_scaled_time, vdf_normed_time,
                                   grid_cart, grid_spher, grid_cyl,
                                   time_interp, grid_geom)

        return self._obj

    def _preprocess_data(self, species):
        """
        Numpyse the loaded data, and pre-format them: time averaging or
        interpolating data of different time resolution, frame management, etc.
        """

        if self.settings['mode'] == 'low_res':
            mode_mms_vdf = 'fast'
        elif self.settings['mode'] == 'high_res':
            mode_mms_vdf = 'brst'

        if len(self.settings['probes']) > 1:
            raise NotImplementedError('VDF interpolations are only implemented\
                                       for one probe at a time for now.')
        probe_ID = self.settings['probes'][0]

        if species == 'ion':
            spec_key = 'i_dist{}'.format(probe_ID)
            spec_mms_vdf = 'dis'
            m = 1.660538e-27  # kg
            e = 1.60217e-19   # C
        elif species == 'electron':
            spec_key = 'e_dist{}'.format(probe_ID)
            spec_mms_vdf = 'des'
            m = 9.10938356e-31  # kg
            e = -1.60217e-19   # C
        else:
            raise ValueError(' In AidaAccessorVDF: variable \'species\' should \
                     be either \'ion\' or \'electron\'')

        vdf0 = self._obj[spec_key].values.copy()
        # Swap energy and longitude angle dimensions to comply with the
        #    ISO standard for spherical coordinate system: (rho, theta, phi).
        vdf0 = np.swapaxes(vdf0, 1, 3)
        time_par = self._obj[spec_key].coords[self._get_time_key(spec_key)].values.copy()
        key_str = 'mms{}_{}_energy_{}'.format(probe_ID, spec_mms_vdf, mode_mms_vdf)
        energy = self._obj[spec_key][key_str].values.copy()
        key_str = 'mms{}_{}_phi_{}'.format(probe_ID, spec_mms_vdf, mode_mms_vdf)
        phi = self._obj[spec_key][key_str].values.copy()
        key_str = 'mms{}_{}_theta_{}'.format(probe_ID, spec_mms_vdf, mode_mms_vdf)
        theta = self._obj[spec_key][key_str].values.copy()
        # Speed vector, m/s. vel.shape = 32x3000
        speed = np.sqrt(2 * energy * np.abs(e) / m)
        nb_vdf = time_par.size
        #
        key_str = 'dc_mag{}'.format(probe_ID)
        B_gse = self._obj[key_str].values[:, :3].T.copy()
        time_B = self._obj[key_str].coords[self._get_time_key(key_str)].values
        B_gse_par = self._time_average(B_gse, time_B, time_par)
        # Going for SI
        vdf0 *= 1.e12   # cm^-6 to m^-6
        B_gse *= 1e-9   # nT to T
        B_gse_par *= 1e-9   # nT to T
        phi *= np.pi / 180    # Degree to radian
        theta *= np.pi / 180    # Degree to radian

        return vdf0, time_par, speed, theta, phi, nb_vdf, B_gse_par

    def _get_time_key(self, variable_key):
        """ Search for the time key, not knowing it's number. """
        for k in self._obj[variable_key].coords:
            if 'time' in k:
                key_time = k
        return key_time

    def _verbosity(self, grid_geom, resolution, interp_schem, time_par,
                  ind_dis_oi, ind_start, ind_stop):
        """
        Some _verbosity for the main method.
        """
        print('\n')
        print('.____________________________________________________________')
        print('| mms_vdf.py, aidapy.')
        print('|')
        print('| Product(s):')
        for p in self.settings['prod']:
            print('|   - {}'.format(p))
        print('| Grid geometry:    {}'.format(grid_geom))
        print('| Resolution:       {}'.format(resolution))
        print('| Interpolation:    {}'.format(interp_schem))
        print('| Start time:       {}'.format(time_par[ind_dis_oi[0]]))
        print('| Stop time :       {}'.format(time_par[ind_dis_oi[-1]+1]))
        print('| Ind. start-stop:  {}-{}'.format(ind_start, ind_stop))
        print('| Nb distributions: {}'.format(len(ind_dis_oi)))
        print('|____________________________________________________________')
        print('\n')

    @staticmethod
    def _check_inputs(time_par, start_time, end_time,
                     start_time_sub, end_time_sub, grid_geom):
        """ Various tests on the interpolation inputs (type, value, etc.) """
        if grid_geom not in ['cart', 'spher', 'cyl']:
            raise NotImplementedError('Coordinate system -- {} -- '
                                      'not implemented.'.format(grid_geom))
        if (date2num(time_par[0]) > date2num(start_time_sub)) or \
           (date2num(time_par[-1]) < date2num(end_time_sub)):
            raise ValueError('The chosen time sub_interval falls partially '
                             'or entirely outside the time interval covered by'
                             ' the file.')
        if date2num(start_time_sub) >= date2num(end_time_sub):
            raise ValueError('The bounds of the time sub-interval are not'
                             ' chrono-logical.')
        if date2num(start_time+timedelta(seconds=60)) > date2num(end_time):
            raise ValueError('The time interval must be larger than one '
                             'minute.')
        #if end_time_sub-start_time_sub<30:
        #    raise ValueError('The chose time sub-interval is shorter than '
        #                     'one FPI measurement.')

    def _init_rotations_matrices(self, time_par, start_time, end_time):
        """ Returns rotations matrices interpolated at time_par.
        """
        probe_ID = self.settings['probes'][0]
        key_str = 'sc_att{}'.format(probe_ID)
        quat_eci_to_gse = self._obj[key_str].values
        time_quat = self._obj[key_str].coords[self._get_time_key(key_str)].values
        ####################
        settings = {'prod': ['sc_att'], 'probes': [probe_ID], 'coords': 'gse',
                    'mode': 'high_res', 'frame':'dbcs'}
        from aidapy import load_data
        xr_mms_tmp = load_data(mission='mms', start_time=start_time, end_time=end_time, **settings)
        quat_eci_to_dbcs = xr_mms_tmp['sc_att{}'.format(probe_ID)].values
        # time_quat2 = self._obj['sc_att1'].coords['time1'].values
        #####################
        f = interp1d(mpl.dates.date2num(time_quat), quat_eci_to_gse.T,
                     bounds_error=False, fill_value=np.nan)
        quat_interp = f(mpl.dates.date2num(time_par))
        itk = np.isnan(quat_interp[0])
        quat_interp[:, itk] = 1.
        r = R.from_quat(quat_interp.T)
        self.R_eci_to_gse = r.as_matrix()
        self.R_gse_to_eci = np.transpose(self.R_eci_to_gse, axes=(0, 2, 1))
        self.R_eci_to_gse[itk] *= np.nan
        self.R_gse_to_eci[itk] *= np.nan
        #
        f = interp1d(mpl.dates.date2num(time_quat), quat_eci_to_dbcs.T,
                     bounds_error=False, fill_value=np.nan)
        quat_interp = f(mpl.dates.date2num(time_par))
        itk = np.isnan(quat_interp[0])
        quat_interp[:, itk] = 1.
        r = R.from_quat(quat_interp.T)
        self.R_eci_to_dbcs = r.as_matrix()
        R_dbcs_to_eci = np.transpose(self.R_eci_to_dbcs, axes=(0, 2, 1))
        self.R_eci_to_dbcs[itk] *= np.nan
        R_dbcs_to_eci[itk] *= np.nan

    def _init_R_b_to_dbcs(self, time_par, B_gse_par):
        """Returns the main rotation matrix, from the frame-of-interest
        aligned with the B-field, to the instrument frame, DBCS.

        Parameters
        ----------
        R_b_to_dbcs
            rotation matrix from b to dbcs (N, 3, 3)
        time_par
            particle timestamps vector, (N,)
        B_gse_par
            B-field in GSE at particles's time, (3, N)

        """
        B_eci_par = np.array([np.dot(self.R_gse_to_eci[i], B_gse_par[:, i])
                              for i in np.arange(time_par.size)]).T
        B_dbcs_par = np.array([np.dot(self.R_eci_to_dbcs[i], B_eci_par[:, i])
                               for i in np.arange(time_par.size)]).T
        R_dbcs_to_b = np.zeros((time_par.size, 3, 3))
        R_b_to_dbcs = np.zeros((time_par.size, 3, 3))
        for i in np.arange(time_par.size):
            R_dbcs_to_b[i] = vdfu.R_2vect(B_dbcs_par[:, i], np.array([0, 0, 1]))
            R_b_to_dbcs[i] = vdfu.R_2vect(np.array([0, 0, 1]), B_dbcs_par[:, i])
        return R_b_to_dbcs, R_dbcs_to_b

    def _init_ibulkv(self, species, time_par):
        """
        Returns the ion bulk velocity at the particles' time in the instrument
        frame DBCS, i.e. either ions or electrons. In the latter case, the
         velocity is linearly interpolated at electrons timestamps.

        Parameters
        ----------
        ibulkv_dbcs_par
            ion bulk velocity in DBCS, (3, N)
        species: str
            species of interest
        time_par:
            timestamps of particles, (N,)
        """
        probe_ID = self.settings['probes'][0]
        ibulk_key = 'i_bulkv{}'.format(probe_ID)
        ibulkv_gse = self._obj[ibulk_key].values.T
        time_i = self._obj[ibulk_key].coords[self._get_time_key(ibulk_key)].values
        if species == 'electron':
            f = interp1d(mpl.dates.date2num(time_i), ibulkv_gse,
                         bounds_error=False, fill_value=np.nan)
            ibulkv_gse_par = f(mpl.dates.date2num(time_par))
        elif species == 'ion':
            ibulkv_gse_par = ibulkv_gse
        ibulkv_eci_par = np.array([np.dot(self.R_gse_to_eci[i], ibulkv_gse_par[:, i])
                                   for i in np.arange(time_par.size)]).T
        ibulkv_dbcs_par = np.array([np.dot(self.R_eci_to_dbcs[i], ibulkv_eci_par[:, i])
                                    for i in np.arange(time_par.size)]).T
        # From km/s to m/s:
        ibulkv_dbcs_par *= 1.e3
        return ibulkv_dbcs_par

    @staticmethod
    def _time_sub_range(nb_vdf, time_par, start_time_sub, end_time_sub):
        """ Select a sub-time-range and the corresponding indices of interest,
            ind_dis_oi: "indices of the vdfutions Of Interest" """
        ind_dis_oi = np.arange(nb_vdf, dtype=int)
        ind_start = np.where(date2num(time_par) > date2num(start_time_sub))[0][0]
        ind_stop = np.where(date2num(time_par) > date2num(end_time_sub))[0][0]
        ind_dis_oi = ind_dis_oi[ind_start: ind_stop]
        return ind_dis_oi, ind_start, ind_stop

    @staticmethod
    def _time_average(v, time_v, time_oi):
        """ Returns a degraded-time-resolution version of v, given on the timestamps
        contained by time_oi. Values are binned and averaged.
        v.shape = (3,t), time_v.shape = (t,) """
        v_av = np.zeros((3, time_oi.size))
        dt = time_oi[1]-time_oi[0]
        time_bins = np.hstack((time_oi-dt*.5, time_oi[-1]+.5*dt))
        itk = (~np.isnan(v[0]))
        stat = scipy.stats.binned_statistic(mpl.dates.date2num(time_v[itk]), v[0, itk],
                                            statistic='mean',
                                            bins=mpl.dates.date2num(time_bins))
        stat.statistic[np.isnan(stat.statistic)] = 0
        v_av[0] = stat.statistic
        stat = scipy.stats.binned_statistic(mpl.dates.date2num(time_v[itk]), v[1, itk],
                                            statistic='mean',
                                            bins=mpl.dates.date2num(time_bins))
        stat.statistic[np.isnan(stat.statistic)] = 0
        v_av[1] = stat.statistic
        stat = scipy.stats.binned_statistic(mpl.dates.date2num(time_v[itk]), v[2, itk],
                                            statistic='mean',
                                            bins=mpl.dates.date2num(time_bins))
        stat.statistic[np.isnan(stat.statistic)] = 0
        v_av[2] = stat.statistic
        return v_av

    @classmethod
    def _transform_grid(cls, grid_cart, R_b_to_dbcs, ibulkv_dbcs_par, frame):
        """Transforms the grid from the frame of interest to the
        instrument frame. Returns the grid expressed in the spherical system.

        Parameters
        ----------
        grid_s
            the transformed grid, in spherical coordinates, (3, N, N, N)
        grid_cart
            cartesian interpolation grid, (3, N, N, N)
        R_b_to_dbcs
            rotation matrix from B to DBCS, (3, 3)
        ibulkv_dbcs_par
            ion bulk velocity at particles' time, (3,)
        frame: str
            frame of interest.
        """
         # This copy of grid_cart will be rotated, every scan differently.
        grid_c = grid_cart.copy()
        # For now grid_c is in the frame of interest, EB, GSE, or any.
        if frame == 'instrument':
            pass
        elif frame == 'B':
            grid_c = np.dot(R_b_to_dbcs, grid_c.reshape(3, -1)).reshape(grid_cart.shape) ## Rotation.
            grid_c += ibulkv_dbcs_par[:, None, None, None] ## Translation.
        else:
            raise ValueError('{}: unknown frame.'.format(frame))
        # We now go for the spherical system, the natural instrument
        #     coordinate system. Here, the -1 is reversing velocity vector to
        #     viewing direction, in which the instrument tables are expressed.
        grid_s = vdfu.cart2spher(-1*grid_c)
        return grid_s

    @staticmethod
    def _interpolate_spher_mms(vdf0, speed, theta, phi, grid_s, interp_schem):
        """Interpolates particles' VDF, tailored for MMS data."""
        vdf_interp_shape = grid_s.shape[1:]
        # Preparing the interpoplation.
        phi_period = np.zeros(34)
        phi_period[1:-1] = phi
        phi_period[0] = phi[-1] - 2 * np.pi
        phi_period[-1] = phi[0] + 2 * np.pi
        theta_period = np.zeros(18)
        theta_period[1:-1] = theta
        theta_period[0] = theta[-1] - np.pi
        theta_period[-1] = theta[0] + np.pi
        vdf_period = np.zeros((32, 18, 34))
        vdf_period[:, 1:-1, 1:-1] = vdf0
        vdf_period[:, 1:-1, 0] = vdf0[:, :, -1]
        vdf_period[:, 1:-1, -1] = vdf0[:, :, 0]
        vdf_period[:, 0] = vdf_period[:, 1]
        vdf_period[:, 17] = vdf_period[:, 16]
        itkR = ~np.isnan(speed)
        if 0:   ## For "partial" moments.
            itkRtmp = speed < 4e6
            vdf_period[itkRtmp] = 0.
        # INTERPOLATION!

        if interp_schem in ['near', 'lin']:

            if interp_schem == 'near':
                interp_schem_str = 'nearest'
            elif interp_schem == 'lin':
                interp_schem_str = 'linear'

            interp_func = RegularGridInterpolator((speed[itkR], theta_period,
                                                   phi_period),
                                                  (vdf_period[itkR]),
                                                  bounds_error=False,
                                                  method=interp_schem_str,
                                                  fill_value=np.nan)
            d = interp_func(grid_s.reshape(3, -1).T)
            d = d.T.reshape(vdf_interp_shape)  # (res,res,res)

        elif interp_schem == 'cub':
            if not tricubic_imported:
                raise NotImplementedError('The tricubic module was not found. '
                                          'Try: pip install tricubic')

            d = np.zeros(vdf_interp_shape).flatten()
            ip = tricubic.tricubic(list(vdf_period),
                                   [vdf_period.shape[0],
                                    vdf_period.shape[1],
                                    vdf_period.shape[2]])
            ds = speed[1:]-speed[:-1]
            delta_theta = theta[1]-theta[0]
            delta_phi = phi[1]-phi[0]
            vMin_theta = 0.
            vMin_phi = 0.
            #
            bi = np.digitize(grid_s[0], speed)-1
            grid_s[0] = bi + (grid_s[0]-speed[bi])/ds[bi]
            grid_s[1] = (grid_s[1]-vMin_theta)/delta_theta + .5
            grid_s[2] = (grid_s[2]-vMin_phi)/delta_phi + .5
            for j, node in enumerate(grid_s.reshape((3, -1)).T):
                d[j] = ip.ip(list(node))
            d = d.reshape(vdf_interp_shape)
            # "fill_value". Should also be done for values larger than,
            # and not only smaller than.
            d[grid_s[0] < 0] = np.nan
        return d

    def _save_xarray_variables(self, vdf_interp, vdf_scaled, vdf_normed,
                              vdf_interp_time, vdf_scaled_time, vdf_normed_time,
                              grid_cart, grid_spher, grid_cyl,
                              time_interp, grid_geom):
        """Creating and adding variables to the xarray dataset"""
        try:
            self._obj = self._obj.drop('vdf_interp_time')
            self._obj = self._obj.drop('vdf_interp')
            self._obj = self._obj.drop('grid_interp_cart')
            self._obj = self._obj.drop('grid_interp_spher')
            self._obj = self._obj.drop('grid_interp_cyl')
            self._obj = self._obj.drop('time_interp')
            self._obj = self._obj.drop('vdf_scaled_time')
            self._obj = self._obj.drop('vdf_normed_time')
            self._obj = self._obj.drop('vdf_scaled')
            self._obj = self._obj.drop('vdf_normed')
            self._obj = self._obj.drop('grid_geom')
        except (ValueError, KeyError) as e:
            pass

        if grid_geom == 'spher':
            xrdit = xr.DataArray(vdf_interp_time, dims=['time', 'speed', 'phi'])
            xrdst = xr.DataArray(vdf_scaled_time, dims=['time', 'speed', 'phi'])
            xrdnt = xr.DataArray(vdf_normed_time, dims=['time', 'speed', 'phi'])
            xrdi = xr.DataArray(vdf_interp, dims=['speed', 'theta', 'phi'])
            xrds = xr.DataArray(vdf_scaled, dims=['speed', 'theta', 'phi'])
            xrdn = xr.DataArray(vdf_normed, dims=['speed', 'theta', 'phi'])
            self._obj['vdf_interp_time'] = xrdit
            self._obj['vdf_scaled_time'] = xrdst
            self._obj['vdf_normed_time'] = xrdnt
            self._obj['vdf_interp'] = xrdi
            self._obj['vdf_scaled'] = xrds
            self._obj['vdf_normed'] = xrdn
        elif grid_geom == 'cart':
            xrdit = xr.DataArray(vdf_interp_time, dims=['time', 'vx', 'vz'])
            xrdi = xr.DataArray(vdf_interp, dims=['vx', 'vy', 'vz'])
            self._obj['vdf_interp_time'] = xrdit
            self._obj['vdf_interp'] = xrdi
        elif grid_geom == 'cyl':
            xrdit = xr.DataArray(vdf_interp_time, dims=['time', 'v_perp', 'v_para'])
            xrdi = xr.DataArray(vdf_interp, dims=['v_perp', 'phi', 'v_para'])
            self._obj['vdf_interp_time'] = xrdit
            self._obj['vdf_interp'] = xrdi

        xr_grid_c = xr.DataArray(grid_cart, dims=['v', 'vx', 'vy', 'vz'])
        self._obj['grid_interp_cart'] = xr_grid_c
        xr_grid_s = xr.DataArray(grid_spher, dims=['v', 'speed', 'theta', 'phi'])
        self._obj['grid_interp_spher'] = xr_grid_s
        xr_grid_cy = xr.DataArray(grid_cyl, dims=['v', 'v_perp', 'phi', 'v_para'])
        self._obj['grid_interp_cyl'] = xr_grid_cy
        xr_time = xr.DataArray(time_interp, dims=['time'])
        self._obj['time_interp'] = xr_time
        self._obj['grid_geom'] = grid_geom

    def plot(self, ptype='1d', plt_contourf=False, cmap='RdBu_r'):
        """Calls to plotting methods from aidapy.tools.vdf_plot
        """

        grid_geom = self._obj['grid_geom'].values
        raise_error = False

        if ptype == '1d':
            if grid_geom == 'spher':
                vplt.profiles_1d(self._obj['vdf_interp'].values,
                                 self._obj['grid_interp_spher'].values)
            else:
                raise_error = True

        elif ptype == '3d_time':
            if grid_geom == 'spher':
                vplt.spher_time(self._obj['vdf_interp_time'].values,
                                self._obj['vdf_scaled_time'].values,
                                self._obj['vdf_normed_time'].values,
                                self._obj['grid_interp_spher'].values,
                                self._obj['time_interp'].values,
                                plt_contourf=plt_contourf, cmap=cmap)
            else:
                raise_error = True

        elif ptype == '3d':#to be integrated in vplt.spher!
            if grid_geom == 'cart':
                vplt.cart(self._obj['vdf_interp'].values,
                          self._obj['grid_interp_cart'].values,
                          plt_contourf=plt_contourf, cmap=cmap)
            else:
                raise_error = True

        elif ptype == '2d':
            if grid_geom == 'spher':
                vplt.spher(self._obj['vdf_interp'].values,
                           self._obj['grid_interp_cart'].values,
                           plt_contourf=plt_contourf, cmap=cmap)
            else:
                raise_error = True

        elif ptype == '3d_gyro':
            if grid_geom == 'spher':
                vplt.gyro(self._obj['vdf_interp'].values,
                          self._obj['grid_interp_spher'].values,
                          self._obj['grid_interp_cart'].values,
                          cmap=cmap)
            else:
                raise_error = True

        else:
            raise ValueError('Plot type {} does not exists.'.format(ptype))

        if raise_error:
            raise ValueError('Plot type {} not available for grid '
                             'geometry {}'.format(ptype, grid_geom))
