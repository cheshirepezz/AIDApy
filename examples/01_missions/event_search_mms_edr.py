from datetime import datetime
import numpy as np
from aidapy import event_search

# Time interval
start_time = datetime(2017, 8, 20, 2, 0, 0)
end_time = datetime(2017, 8, 20, 2, 10, 0)
# Input criteria on B,J,|Ve|,dt for reconnection events
settings = {"criteria": lambda dc_mag_tot, j_curl_tot, e_bulkv_x: (np.any(dc_mag_tot < 5)) &
            (np.any(j_curl_tot > 70)) & (np.any(np.abs(e_bulkv_x) > 4000)),
            "parameters": {"mission": "mms",
                           "process": "edr",
                           "probes": ['1'],
                           "mode": "brst",
                           "time_window": 120,
                           "time_step": 120}}
# time_gap defines the time gap inside which the times are considered
# to belong to the same event

event_search(settings, start_time, end_time)
