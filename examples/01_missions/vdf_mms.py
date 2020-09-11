# -*- coding: utf-8 -*-
"""
Example on how to load, analyse and visualise MMS Velocity Distribution Functions.

@author: etienne.behar
"""
from datetime import datetime

from aidapy import load_data

# Time Interval
start_time = datetime(2019, 3, 8, 13, 54, 53)
end_time = datetime(2019, 3, 8, 13, 57, 00)

# settings may contain the keys here-above (for now).
settings = {'prod': ['i_dist', 'e_dist', 'dc_mag', 'sc_att', 'i_bulkv'],
            'probes': ['1'], 'coords': 'gse', 'mode': 'high_res', 'frame': 'gse'}

# Download and load desired data as aidapy timeseries.
xr_mms = load_data(mission='mms', start_time=start_time, end_time=end_time, **settings)

# Interpolation parameters.
# Species can be electron or ion
species = 'electron'
# Chosen frame for the analysis. Only 'instrument' and 'B' for now.
frame = 'B'
# 'cart', 'spher' or 'cyl'.
grid_geom = 'spher'
# Maximum speed in m/s that the grid-of-interest will cover.
v_max = 1.2e7
# Resolution of the grid-of-interest.
resolution = 120
# Interpolation scheme, 'near' for nearest-neighbour (scipy),
#    'lin' for trilinear (scipy), 'cub' for tricubic (need specific install).
interp_schem = 'lin'
# Sub-interval of time.
start_time_sub = datetime(start_time.year, start_time.month, start_time.day,
                          13, 56, 23, 160000)
end_time_sub = datetime(start_time.year, start_time.month, start_time.day,
                        13, 56, 23, 225000)

xr_mms = xr_mms.vdf.interpolate(
    start_time, end_time, start_time_sub, end_time_sub, species=species,
    frame=frame, grid_geom=grid_geom, v_max=v_max, resolution=resolution,
    interp_schem=interp_schem)

xr_mms.vdf.plot('1d')
xr_mms.vdf.plot('2d', plt_contourf=True)
xr_mms.vdf.plot('3d_gyro')
xr_mms.vdf.plot('3d_time', plt_contourf=False)

grid_geom = 'cart'
species = 'ion'
interp_schem = 'lin'
resolution = 80
v_max = 8.e5
start_time_sub = datetime(start_time.year, start_time.month, start_time.day,
                          13, 56, 14, 0)
end_time_sub = datetime(start_time.year, start_time.month, start_time.day,
                        13, 56, 20, 0)

xr_mms = xr_mms.vdf.interpolate(
    start_time, end_time, start_time_sub, end_time_sub, species=species,
    frame=frame, grid_geom=grid_geom, v_max=v_max, resolution=resolution,
    interp_schem=interp_schem)
#
xr_mms.vdf.plot('3d')
