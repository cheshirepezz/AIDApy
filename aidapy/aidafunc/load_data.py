"""Loading data functions

This script contains the function load_data needed to make the interface
with the user and also the associated functions for the check.

This file can be imported as a module and contains the following
functions:
"""

import datetime
import xarray as xr
from astropy.time import Time
import warnings

from aidapy.data.mission.mission import Mission
from aidapy.aidaxr import process


def load_data(mission, start_time, end_time, **kwargs):
    """
     Select the appropriate TimeSeries from the given arguments.

    Parameters
    ----------
    mission : str
        The name of the mission from which the data are loaded/downloaded

    start_time : ~datetime.datetime or ~astropy.time.Time
        Start time of the loading

    end_time : ~datetime.datetime or ~astropy.time.Time
        End time of the loading

    **kwargs
        Specific arguments for providing information for the mission or
        the download settings: probes, coordinates, product, mode, etc.

    Return
    ------
    xarray_mission : ~xarray.DataSet
        Requested data contained within a xarray DataSet. Each data variable
        contains a specific product of a specific probe
    """
    _check_time(start_time, end_time)
    prod = kwargs.get('prod', None)
    probes = kwargs.get('probes', None)
    coords = kwargs.get('coords', None)
    mode = kwargs.get('mode', None)
    frame = kwargs.get('frame', None)

    try:
        mission_instance = Mission(mission, start_time, end_time)
    except ValueError:
        raise ValueError('The mission {} is not yet'
                         ' implemented'.format(mission))

    prod_list = []
    data_settings = get_mission_info(mission, hide=True)['data_settings']

    # Check if prod type are available
    if not prod:
        pass
    else:
        for data_type in prod:
            if data_type in data_settings:
                prod_list.append(data_type)

    mission_params = {'mission': mission}

    if prod_list:
        xarray_dict = mission_instance.download_data(prod_list, probes,
                                                     coords, mode, frame)
    elif not prod:
        xarray_dict = mission_instance.download_data(None, probes, coords,
                                                     mode, frame)
    else:
        xarray_dict = {}

    # compute extra (L3) data
    if prod:
        prod_not_registered = list(set(prod)-set(prod_list))
        for l3_prod in prod_not_registered:
            if hasattr(_L3Preprocess, l3_prod):
                func = getattr(_L3Preprocess, l3_prod)
                data_temp = func(mission_instance, prod, probes, coords, mode,
                                 xarray_dict, mission_params)
                xarray_dict.update(data_temp)
            else:
                raise ValueError(
                    '{0} is not an available data product'.format(prod))

    xarray_mission = _convert_dict_to_ds(xarray_dict, mission_params)
    xarray_mission.attrs['load_settings'] = kwargs
    return xarray_mission


def get_mission_info(mission='mission', start_time=None, end_time=None,
                     product=None, full_data_settings=False, hide=False):
    """
     Provide information on the mission

    Parameters
    ----------
    mission : str
        The name of the mission from which the data are loaded/downloaded

    start_time : ~datetime.datetime or ~astropy.time.Time
        Start time of the loading

    end_time : ~datetime.datetime or ~astropy.time.Time
        End time of the loading

    product : str
        Data product to look for in data_settings

    full_data_settings : bool
        Tag to provide all available keys

    hide : bool
        Tag to hide print messages when use in routines

    Return
    ------
    info : dict or str
        String containing the AIDApy keyword of the queried product
        or
        Dictionary with information on the mission or queried product
        with the following keys:
        - name:
        - allowed_probes:
        - data_settings:
    """
    if (start_time and not end_time) or (not start_time and end_time):
        raise ValueError('either start_time and end_time must be defined '
                         'or none of them.')
    if start_time is None and end_time is None:
        # Fake start_time and end_time
        start_time = datetime.datetime(2017, 1, 1, 1, 0, 0)
        end_time = datetime.datetime(2017, 1, 1, 1, 1, 0)
    mission_instance = Mission(mission, start_time, end_time)
    mission_instance.concrete_mission.set_probes(
        mission_instance.concrete_mission.allowed_probes)
    settings = mission_instance.get_info_on_mission()

    if product:
        try:
            info = [x for x in settings['data_settings'].keys()
                    if product.casefold() in
                    settings['data_settings'][x]['descriptor'].casefold()]

        except IndexError:
            raise ValueError(f"Data product not recognized. Data products "
                             f"currently available: ",
                             [settings['data_settings'][x]['descriptor']
                              for x in settings['data_settings']])

        else:
            if full_data_settings:
                info = dict(zip(info, [settings['data_settings'][str(x)]
                                       for x in info]))
                if not hide:
                    print("All available keys for data products containing '"
                          + product + "': ")
            else:
                if not hide:
                    print("All available keywords for data products"
                          " containing '" + product + "': ")
            return info

    if not full_data_settings:
        settings['data_settings'] = list(settings['data_settings'].keys())
        info = settings
        if not hide:
            print("All available keywords for "
                  + mission + " mission data products: ")
    else:
        info = settings
        if not hide:
            print("All available keys for "
                  + mission + " mission data products: ")

    return info


def _check_time(start_time, end_time):
    """
    Checking the start and end time.

    Parameters
    ----------
    start_time : `~datetime.datetime` or ~astropy.time.Time

    end_time : ~datetime.datetime` or ~astropy.time.Time

    """
    if (isinstance(start_time, datetime.datetime)
        and isinstance(end_time, datetime.datetime)) or\
       (isinstance(start_time, Time) and isinstance(end_time, Time)):
        if start_time > end_time:
            raise ValueError('start_time must be before end_time')
    else:
        raise ValueError('start_time and end_time must have '
                         'the same format and must be either '
                         'datetime.datetime or astropy.time.Time')


def _convert_dict_to_ds(dict_da, params):
    """
    This method checks the downloaded data and
    convert the dict of xr dataarray into xr dataset

    Parameters
    ----------
    dict_da : a dictionary of xarrays returned from a specific mission

    params : dict
        A dict containing the name of the mission

    Return
    ------
    xr_ds : `~xarray.DataSet`
    """
    if not isinstance(dict_da, dict) or not isinstance(params, dict):
        raise ValueError

    # Check if all value in the dict_x are DataArray
    if not all(isinstance(value_da, xr.DataArray) for value_da in dict_da.values()):
        raise ValueError('All value in the dictionnary must be xrray.DataArray')

    renamed_dict_da = _rename_time_index(dict_da)
    _check_all_dim(renamed_dict_da)

    xr_ds = xr.Dataset(renamed_dict_da)
    # Overall attrs of the Dataset. For the moment this is only the name
    # but it can be extended
    xr_ds.attrs['mission'] = params['mission']

    return xr_ds


def _rename_time_index(dict_da):
    """Rename the dim time of each datarray to ensure proper merge.
    Each time dim is associated to its probe.

    Parameters
    ----------
    dict_da : a dictionary of timeserie datarray

    Return
    ------
    new_dict : dict
        A dictionary of renamed DataArray
    """
    new_dict = {}
    for i, (key, xr_da) in enumerate(dict_da.items()):
        renamed_xr_da = xr_da.rename({'time': 'time{}'.format(i+1)})
        new_dict[key] = renamed_xr_da
    return new_dict


def _check_all_dim(dict_xa):
    """Check if all dims of the dictionnary of xr DataArray are different.
    It ensures a proper merge into xr Dataset without NaN or weird behavior.

    Parameters
    ----------
    dict_da : a dictionary of timeserie datarray
    """
    dim_list_tuple = [xr_da.dims for xr_da in dict_xa.values()]
    dim_full_list = [item for dim_tuple in dim_list_tuple for item in dim_tuple]
    dim_unique = set(dim_full_list)
    if not len(dim_full_list) == len(dim_unique):
        raise ValueError('The dim of each DataArray in the dict must be unique')


class _L3Preprocess(object):

    @staticmethod
    def j_curl(mission_instance, prod, probes, coords, mode, data, mission_params):
        # TODO: Pass the different products from settings (ex. j_vec, j_abs) that can be computed by this function
        #  and return the queried one at the end (or do this in the get_event module)

        xarray_dict = {}
        prod = ['dc_mag']
        all_probes = ['1', '2', '3', '4']

        if data and 'dc_mag1' in data and 'dc_mag2' in data and 'dc_mag3' in data and 'dc_mag4' in data:
            pass
        else:
            data = mission_instance.download_data(prod, all_probes, coords, mode)

        xarray_mission = _convert_dict_to_ds(data, mission_params)
        xarray_mission = xarray_mission.process.reindex_ds_timestamps()
        for probe in probes:
            xarray_dict['j_curl'+probe] = xarray_mission.process.j_curl()
        return xarray_dict

    @staticmethod
    def mag_elangle(mission_instance, prod, probes, coords, mode, data, mission_params):
        # TODO: Pass the different products from settings (ex. j_vec, j_abs) that can be computed by this function
        #  and return the queried one at the end (or do this in the get_event module)

        xarray_dict = {}
        prod = ['dc_mag']

        if data and 'dc_mag' in str(list(data.keys())):
            pass
        else:
            data = mission_instance.download_data(prod, probes, coords, mode)

        for probe in probes:
            xarray_dict['mag_elangle'+probe] = data['dc_mag'+probe].process.elev_angle()
        return xarray_dict

    @staticmethod
    def i_beta(mission_instance, prod, probes, coords, mode, data, mission_params):
        # TODO: Pass the different products from settings (ex. j_vec, j_abs) that can be computed by this function
        #  and return the queried one at the end (or do this in the get_event module)

        xarray_dict = {}
        prod = ['dc_mag', 'i_dens', 'i_temppara', 'i_tempperp']

        if data and 'dc_mag' in str(list(data.keys())) and\
                'i_dens' in str(list(data.keys())) and\
                'i_temppara' in str(list(data.keys())) and\
                'i_tempperp' in str(list(data.keys())):
            pass
        else:
            data = mission_instance.download_data(prod, probes, coords, mode)
            data = _convert_dict_to_ds(data, mission_params)
            data = data.process.reindex_ds_timestamps()

        for probe in probes:
            xarray_dict['i_beta'+probe] = data.process.plasma_beta(probe, 'i')
        return xarray_dict

    @staticmethod
    def e_beta(mission_instance, prod, probes, coords, mode, data, mission_params):
        # TODO: Pass the different products from settings (ex. j_vec, j_abs) that can be computed by this function
        #  and return the queried one at the end (or do this in the get_event module)

        xarray_dict = {}
        prod = ['dc_mag', 'e_dens', 'e_temppara', 'e_tempperp']

        if data and 'dc_mag' in str(list(data.keys())) and\
                'e_dens' in str(list(data.keys())) and\
                'e_temppara' in str(list(data.keys())) and\
                'e_tempperp' in str(list(data.keys())):
            pass
        else:
            data = mission_instance.download_data(prod, probes, coords, mode)
            data = _convert_dict_to_ds(data, mission_params)
            data = data.process.reindex_ds_timestamps()

        for probe in probes:
            xarray_dict['e_beta'+probe] = data.process.plasma_beta(probe, 'e')
        return xarray_dict
