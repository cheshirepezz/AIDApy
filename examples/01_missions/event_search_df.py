from datetime import datetime
import numpy as np
from aidapy import event_search

# Time interval
start_time = datetime(2017, 7, 15, 7, 0, 0)
end_time = datetime(2017, 7, 15, 12, 0, 0)

# Input settings to look for dipolarization fronts on MMS1 probe
settings = {
    "criteria": lambda dc_mag_z, mag_elangle, sc_pos_x, sc_pos_y:
    (np.where(dc_mag_z == np.max(dc_mag_z))[0] > np.where(dc_mag_z == np.min(dc_mag_z))[0]) &
    (np.abs(mag_elangle[np.where(dc_mag_z == np.min(dc_mag_z))[0]] - mag_elangle[np.where(dc_mag_z == np.max(dc_mag_z))[0]]) > 10) &
    (np.any(mag_elangle > 45)) & (np.all(sc_pos_x <= -5 * 6378)) & (np.all(np.abs(sc_pos_y) <= 15 * 6378)),
    "parameters": {"mission": "mms",
                   "process": "df",
                   "probes": ['1'],
                   "time_window": 306,
                   "coords": "gse",
                   "mode": 'low_res',
                   "time_step": 306,
                   "sample_freq": 1}}

event_search(settings, start_time, end_time, plot=True)
