"""
Test for mms_vdf methods.
"""
from datetime import datetime
import numpy as np
import pytest
from aidapy import load_data


def test_vdf_mms():
    '''Integration test on a complete interpolation.'''
    start_time = datetime(2019, 3, 8, 13, 54, 53)
    end_time = datetime(2019, 3, 8, 13, 57, 00)
    settings = {'prod': ['i_dist', 'dc_mag', 'sc_att', 'i_bulkv'],
                'probes': ['1'], 'coords': 'gse', 'mode': 'high_res', 'frame':'gse'}
    xr_mms = load_data(mission='mms', start_time=start_time, end_time=end_time, **settings)
    species = 'ion'
    frame = 'B'
    grid_geom = 'spher'
    v_max = 8.e5
    resolution = 60
    interp_schem = 'lin'
    start_time_sub = datetime(start_time.year, start_time.month, start_time.day,
                              13, 56, 23, 160000)
    end_time_sub = datetime(start_time.year, start_time.month, start_time.day,
                            13, 56, 24, 225000)
    xr_mms = xr_mms.vdf.interpolate(start_time, end_time, start_time_sub, end_time_sub,
                                    species=species, frame=frame, grid_geom=grid_geom,
                                    v_max=v_max, resolution=resolution, interp_schem=interp_schem,
                                    verbose=False)
    target = np.array([1.7031225e-10, 1.5537861e-10, 1.4097469e-10, 1.4718438e-10, 3.0006439e-10,
                       1.6751817e-10, 1.2765614e-10]).astype(np.float32)
    result = np.nanmean(xr_mms['vdf_interp_time'].values, axis=(1, 2)).astype(np.float32)
    # This test will potentially fail if MMS data are updated...
    assert np.allclose(target, result, atol=1.e-24)

