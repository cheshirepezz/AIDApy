"""
The following test integration suite assesses the interconectivity between
 aidafunc, mission subpackage, and HelioPy
"""
import pytest
from datetime import datetime
import numpy as np
import astropy.units as u

from aidapy import load_data


def test_omni():
    start_time = datetime(1970, 1, 1, 0, 0, 0)
    end_time = datetime(1970, 1, 3, 0, 0, 0)
    settings = {'prod': ['dc_mag']}
    xr_omni = load_data(mission='omni', start_time=start_time,
                        end_time=end_time, **settings)
    omni_b_x = xr_omni['dc_mag1'].sel(products='BX_GSE').values
    omni_b_x_units = omni_b_x * u.Unit(
        xr_omni['dc_mag1'].attrs['Units']['BX_GSE'])
    target = np.array([
        -1.4, -0.3, -2.5, -1.2, -3.5, -2.5, -0.5, -1.6, -2.4, -2.4,
        -1.7, -1.5, -0.8, -4.4, -4.8, -3.6, -6.3, -6.7, -1.4, -2.7, 0.8,
        0.8, -0.4, -4.4, -5.4, -6.2, -6.3, -4.2, -8.1, -7., -2.2, -5.2,
        -2.6, -8.4, -5.7, -2.1, -2.7, -1.1, 0., -3.8, -4.7, -1.5, -0.9,
        -1.3, -2.9, -2., -3.2
    ]) * u.nT
    assert u.allclose(target, omni_b_x_units)


def test_omni_default():
    start_time = datetime(1970, 1, 1, 0, 0, 0)
    end_time = datetime(1970, 1, 3, 0, 0, 0)
    xr_omni = load_data(mission='omni', start_time=start_time,
                        end_time=end_time)
    try:
        xr_omni['all1']
    except:
        raise ValueError


@pytest.mark.skip(reason="Fails in the CI tools")
def test_cluster():
    start_time = datetime(2004, 6, 18, 11, 35, 0)
    end_time = datetime(2004, 6, 18, 11, 36, 0)
    settings = {'probes': ['3'], 'prod': ['dc_mag']}
    xr_cluster = load_data('cluster', start_time, end_time, **settings)
    cluster_b_x = xr_cluster['dc_mag3'].sel(
        B_vec_xyz_gse__C3_CP_FGM_SPIN='x').values
    cluster_b_x_units = cluster_b_x * u.Unit(
        xr_cluster['dc_mag3'].attrs['Units']['B_vec_xyz_gse__C3_CP_FGM_SPIN'])
    target = np.array([26.827, 27.212, 27.296, 27.799, 28.264, 28.686, 28.911,
                       29.206, 29.473, 29.483, 29.597, 29.73, 29.896,
                       30.127]) * u.nT
    assert u.allclose(target, cluster_b_x_units)


def test_mms():
    start_time = datetime(2018, 4, 8, 0, 0, 0)
    end_time = datetime(2018, 4, 8, 0, 0, 10)
    settings = {'probes': ['1'], 'prod': ['dc_mag']}
    xr_mms = load_data('mms', start_time, end_time, **settings)
    mms_b_x = xr_mms['dc_mag1'].sel(mms1_fgm_b_gse_srvy_l2='x').values
    mms_b_x_units = mms_b_x * u.Unit(
        xr_mms['dc_mag1'].attrs['Units']['mms1_fgm_b_gse_srvy_l2'])
    target = np.array([1.712529, 1.7148426, 1.7108021, 1.7265971, 1.7372726,
                       1.7345928, 1.7192012, 1.7152323, 1.7145348, 1.718118,
                       1.7249706, 1.7225785, 1.7281982, 1.7349572, 1.7244626,
                       1.7399646, 1.7466872, 1.7412337, 1.762651, 1.7680929,
                       1.7699757, 1.7411137, 1.7634461, 1.7464956, 1.7357976,
                       1.7537696, 1.7317536, 1.7466614, 1.7381922, 1.7112942,
                       1.717961, 1.7125505, 1.7319726, 1.7341373, 1.7375633,
                       1.7236018, 1.7285287, 1.7272918, 1.7329324, 1.7352072,
                       1.7432857, 1.7374923, 1.7280098, 1.7234732, 1.734949,
                       1.7194895, 1.7201461, 1.7266002, 1.6997541]) * u.nT
    assert u.allclose(target, mms_b_x_units)
