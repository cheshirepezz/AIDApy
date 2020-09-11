# -*- coding: utf-8 -*-
"""
This example shows for MMS missionhow:
- to download data
- to build the associated timeseries
- to plot mission data

@author: hbreuill
"""
from datetime import datetime

#AIDApy Modules
from aidapy import load_data
import aidapy.aidaxr


###############################################################################
# Define data parameters
###############################################################################
start_time = datetime(2018, 4, 8, 0, 0, 0)
end_time = datetime(2018, 4, 8, 0, 1, 0)

# Dictionary of data settings: mission, product, probe, coordinates
# Currently available products: 'dc_mag', 'i_dens', and 'all'
settings = {'prod': ['dc_mag'], 'probes': ['1', '2'], 'coords': 'gse'}

###############################################################################
# Download and load desired data as aidapy timeseries
###############################################################################
xr_mms = load_data(mission='mms', start_time=start_time, end_time=end_time, **settings)#, prod=['dc_mag'], probes=['1', '2'], coords='gse')
print(xr_mms['dc_mag1'])
###############################################################################
# Plot the loaded aidapy timeseries
###############################################################################
xr_mms['dc_mag1'].graphical.peek()
