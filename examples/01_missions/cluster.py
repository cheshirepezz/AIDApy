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
# Time Interval
start_time = datetime(2009, 4, 1, 0, 0, 0)
end_time = datetime(2009, 4, 2, 0, 0, 0)

# Dictionary of data settings: mission, product, probe, coordinates
# Currently available products: 'dc_mag', 'i_dens', and 'all'
cl_settings = {'prod': ['i_bulkv'], 'probes': ['1'], 'coords': 'gse'}

###############################################################################
# Download and load desired data as aidapy timeseries
###############################################################################
xr_cluster = load_data('cluster', start_time, end_time, **cl_settings)
print(xr_cluster)
print(xr_cluster['i_bulkv1'])

###############################################################################
# Plot the loaded aidapy timeseries
###############################################################################
xr_cluster['i_bulkv1'].graphical.peek()


