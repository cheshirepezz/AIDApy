# -*- coding: utf-8 -*-
"""
This example shows for OMNI mission how:
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
start_time = datetime(2008, 5, 15, 0, 0, 0)
end_time = datetime(2008, 5, 16, 0, 0, 0)

###############################################################################
# Download and load desired data as aidapy timeseries
###############################################################################
#ts_data = TimeSeries(mission=settings['mission'], dl_settings=settings)
xr_omni = load_data(mission='omni', start_time=start_time, end_time=end_time)
print(xr_omni)
#print(xr_omni['all1'])

###############################################################################
# Plot the loaded aidapy timeseries
###############################################################################
#xr_omni['all1'].graphical.peek()
