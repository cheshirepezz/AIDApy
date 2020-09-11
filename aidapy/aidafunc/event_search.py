import logging
import timeit
import inspect
import more_itertools

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

from .load_data import load_data
# logging.basicConfig(level=logging.INFO)


def event_search(settings, start_time=None, end_time=None, plot=False,
                 to_file=False):
    """
    Threshold-based search for events of specific scientific processes

    Parameters
    ----------
    settings : dict
        Dictionnary containing the search parameters

    start_time : ~datetime.datetime or ~astropy.time.Time
        Start time of the search

    end_time : ~datetime.datetime or ~astropy.time.Time
        End time of the search

    plot : bool, default False
        Whether to plot the found events

    to_file : bool, default False
        Whether to write a file containing the list of found events

    Return
    ----------
    data : ~xarray.Dataset
        Dataset of products considered in the settings

    events : list
        List of events fulfilling the input criteria
    """
    tic = timeit.default_timer()

    # If no start or end time specified, then browse through the local database
    if not start_time or not end_time:
        raise ValueError('start_time and end_time must be defined')
    else:

        if settings == 'df':
            settings = _settings_df()
        elif settings == 'edr':
            settings = _settings_edr()
        else:
            pass

        data = _load_and_compute_data(start_time, end_time, settings)
        data, events = _get_event(data, settings)

        if plot:
            plot_dataset(data, events)
        if to_file:
            _write_events(data, events)

        toc = timeit.default_timer()
    logging.info('Time of calculation: ' + str((toc - tic) / 3600) + ' h')

    return data, events


def _load_and_compute_data(start_time, end_time, settings):
    """Line plot all products from a dataset.

    Parameters
    ----------
    start_time : datetime instance
    TOFILL

    end_time : datetime instance
    TOFILL

    settings : dict
    TOFILL

    Return
    ------
    data : tofill
        tofill

    """
    # load data
    mission = settings['parameters']['mission']
    probes = settings['parameters']['probes']

    try:
        mode = settings['parameters']['mode']
    except KeyError:
        mode = ''

    try:
        sample_freq = settings['parameters']['sample_freq']
    except KeyError:
        sample_freq = None

    data_vars = list(inspect.signature(
            settings['criteria']).parameters.keys())

    prods = []
    for var in data_vars:
        prods.append(var.split('_')[0]+'_'+var.split('_')[1])

    prods = list(set(prods))

    params = {'prod': prods, 'probes': probes,
              'coords': 'gse', 'mode': mode}
    data = load_data(mission, start_time, end_time, **params)

    data = data.process.reindex_ds_timestamps(sample_freq)


    # # compute extra data
    # prod_not_registered = {x: settings['data'][x]
    #                        for x in set(settings['data']) - set(prod_list)}
    #
    # # TODO: add check on the dataset to see if we can use the routine
    # if data and 'dc_mag1' in data and 'dc_mag2' in data \
    #         and 'dc_mag3' in data and 'dc_mag4' in data:
    #     pass
    # else:
    #     mission = settings['parameters']['mission']
    #     params = {'prod': ['dc_mag'], 'probes': ['1', '2', '3', '4'],
    #               'coords': 'gse', 'mode': 'brst'}
    #     data_ = load_data(mission, start_time, end_time, **params)
    #     data_ = data_.process.reindex_on_smallest_da()
    #
    # for prod in prod_not_registered.keys():
    #     if hasattr(data_.process, prod):
    #         func = getattr(data_.process, prod)
    #         data_temp = func()
    #         data[prod] = data_temp.reindex({'time': data.time},
    #                                        method='nearest')
    #     else:
    #         raise ValueError(
    #             '{0} is not an available L3 data product'.format(prod))

    return data


def plot_dataset(ds, events):
    """
    Line plot of considered data.

    Parameters
    ----------
    ds : ~xarray.Dataset
        Dataset containing the plasma data to plot

    events : list
        List of events found using the event_search function

    """
    # Determine number of rows
    n_rows = len(ds.data_vars)

    fig, axs = plt.subplots(nrows=n_rows, sharex='col')
    rows = ['{}'.format(row) for row in ds.data_vars]

    for i, row in enumerate(ds):
        ds[row].plot.line(x='time', ax=axs[i])
        for j, k in enumerate(events[::2]):
            axs[i].axvspan(ds.time.data[events[j * 2]],
                           ds.time.data[events[j * 2 + 1]], color='y',
                           alpha=0.5, lw=0)
    plt.show()


def _write_events(data, events):
    """Print list of events found in file.

    Parameters
    ----------
    ds : TOFILL

    events : TOFILL

    """
    output = open("events_list.txt", "w")

    output.write("List of events found"+"\n"+"\n")
    output.write("N°, START TIME, END TIME \n")

    for j, k in enumerate(events[::2]):
        output.write(str(j + 1) + ", " + str(data.time.data[events[j * 2]]) +
                     ", " + str(data.time.data[events[j * 2 + 1]]) + "\n")

    output.close()


def _settings_edr():
    """
    Default settings to search for electron diffusion region events

    :return:
    Dictionary of criteria and parameters for EDR events
    """

    settings = {"criteria": lambda dc_mag_tot, j_curl_tot, e_bulkv_x:
                (np.any(dc_mag_tot < 5)) & (np.any(j_curl_tot > 70))
                & (np.any(np.abs(e_bulkv_x) > 4000)),
                "parameters": {"mission": "mms",
                               "process": "edr",
                               "probes": ['1'],
                               "mode": "brst",
                               "time_window": 120,
                               "time_step": 120}}
    return settings


def _settings_df():
    """
    Default settings to search for dipolarization front events

    :return:
    Dictionary of criteria and parameters for DF events
    """

    settings = {
        "criteria": lambda dc_mag_z, mag_elangle, sc_pos_x, sc_pos_y:
        (np.where(dc_mag_z == np.max(dc_mag_z))[0] >
         np.where(dc_mag_z == np.min(dc_mag_z))[0]) &
        (np.abs(mag_elangle[np.where(dc_mag_z == np.min(dc_mag_z))[0]] -
                mag_elangle[np.where(dc_mag_z == np.max(dc_mag_z))[0]]) > 10) &
        (np.any(mag_elangle > 45)) & (np.all(sc_pos_x <= -5 * 6378)) & (
            np.all(np.abs(sc_pos_y) <= 15 * 6378)),
        "parameters": {"mission": "mms",
                       "process": "df",
                       "probes": ['1'],
                       "time_window": 306,
                       "coords": "gse",
                       "mode": 'low_res',
                       "time_step": 306,
                       "sample_freq": 1}}
    return settings


def _get_event(data, settings):
    """tofill

    Parameters
    ----------
    data : tofill
    TOFILL

    settings : tofill
    TOFILL

    Return
    ------
    data : tofill
        tofill

    events : tofill
        tofill

    """
    time = data.time.data
    probes = settings['parameters']['probes']
    # data time resolution in s
    data_res = (data.time.data[1]-data.time.data[0]) / np.timedelta64(1, 's')
    # rolling window size in nb of pts
    win_size = int(settings['parameters']['time_window'] * 1 / data_res)
    delta_t = int(settings['parameters']['time_step'] * 1 / data_res)
    data, data_dict = _reshape_ds(data, settings)
    segs = list(more_itertools.windowed(np.arange(len(time)), int(win_size),
                                        fillvalue='nan', step=delta_t))
    events = []

    for seg in segs[:-1]:
        # TODO: fix problem of the last window (larger than iterable)
        seg = np.array(seg)
        data_array = []

        for var in data:
            data_array.append(data[var].data[seg, int(probes[0])
                                             - 1:int(probes[-1])])

        data_array = np.array(data_array)
        # Where criteria are fulfilled in rolling time window
        ind = np.where(settings['criteria'](*data_array))
        if np.ndim(ind) == 2:
            ind = ind[0]
        if len(ind) == 0:
            continue
        else:
            # TODO: improve selection of event in time window
            events += [seg[0], seg[-1]]

    return data, events


def _reshape_ds(data, settings):
    """tofill

    Parameters
    ----------
    data : tofill
    TOFILL

    settings : tofill
    TOFILL

    Return
    ------
    new_ds : tofill
        tofill

    data_dict : tofill
        tofill

    """
    probes = settings['parameters']['probes']
    new_ds = xr.Dataset({})
    data_dict = {}

    data_vars = list(inspect.signature(
            settings['criteria']).parameters.keys())

    data_prods = []
    for var in data_vars:
        prod = var.split('_')[0]+'_'+var.split('_')[1]
        data_prods.append(prod)
        data_dict[var] = prod

    for k, j in enumerate(data_vars):

        data_array = np.ndarray(shape=(len(data.time.data), len(probes)))

        for l, m in enumerate(probes):
            if 'tot' in j:
                data_array[:, l] = np.linalg.norm(
                    data[data_prods[k]+m].data[:, 0:3], axis=1)
            elif 'x' in j:
                data_array[:, l] = data[data_prods[k]+m].data[:, 0]
            elif 'y' in j:
                data_array[:, l] = data[data_prods[k]+m].data[:, 1]
            elif 'z' in j:
                data_array[:, l] = data[data_prods[k]+m].data[:, 2]
            else:
                data_array[:, l] = data[data_prods[k]+m].data[:]

        new_ds[j] = xr.DataArray(data_array, coords=[data.time, probes],
                                 dims=['time', 'probes'])

    return new_ds, data_dict
