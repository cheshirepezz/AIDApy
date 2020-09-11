"""
Unit tests for mms_vdf methods.
"""
from datetime import datetime, timedelta
import numpy as np
import pytest
from aidapy.aidaxr.vdf import AidaAccessorVDF
import aidapy.tools.vdf_utils as vdfu


def test_check_inputs_a():
    """Unit test on AidaAccessorVDF.check_inputs method.

    Test grid_geom input."""
    time_par = np.arange(datetime(2019, 1, 1), datetime(2019, 1, 2),
                         timedelta(minutes=20)).astype(datetime)
    start_time = datetime(2019, 1, 1, 9)
    end_time = datetime(2019, 1, 1, 15)
    start_time_sub = datetime(2019, 1, 1, 10)
    end_time_sub = datetime(2019, 1, 1, 14)
    grid_geom = 'caart'
    with pytest.raises(Exception):
        AidaAccessorVDF._check_inputs(time_par, start_time, end_time,
                                      start_time_sub, end_time_sub,
                                      grid_geom)


def test_check_inputs_b():
    """Unit test on AidaAccessorVDF.check_inputs method.

    Test sub-range chronology."""
    time_par = np.arange(datetime(2019, 1, 1), datetime(2019, 1, 2),
                         timedelta(minutes=20)).astype(datetime)
    start_time = datetime(2019, 1, 1, 9)
    end_time = datetime(2019, 1, 1, 15)
    start_time_sub = datetime(2019, 1, 1, 14)
    end_time_sub = datetime(2019, 1, 1, 10)
    grid_geom = 'cart'
    with pytest.raises(Exception):
        AidaAccessorVDF._check_inputs(time_par, start_time, end_time,
                                      start_time_sub, end_time_sub,
                                      grid_geom)


def test_check_inputs_c():
    """Unit test on AidaAccessorVDF.check_inputs method.

    Test time sub-range smaller than data time range."""
    time_par = np.arange(datetime(2019, 1, 1), datetime(2019, 1, 2),
                         timedelta(minutes=20)).astype(datetime)
    start_time = datetime(2019, 1, 1, 9)
    end_time = datetime(2019, 1, 1, 15)
    start_time_sub = datetime(2019, 1, 1, 10)
    end_time_sub = datetime(2019, 1, 3, 14)
    grid_geom = 'cart'
    with pytest.raises(Exception):
        AidaAccessorVDF._check_inputs(time_par, start_time, end_time,
                                      start_time_sub, end_time_sub,
                                      grid_geom)
def test_check_inputs_d():
    """Unit test on AidaAccessorVDF.check_inputs method.

    Test global time range larger than 60 seconds."""
    time_par = np.arange(datetime(2019, 1, 1), datetime(2019, 1, 2),
                         timedelta(minutes=20)).astype(datetime)
    start_time = datetime(2019, 1, 1, 9, 0, 0)
    end_time = datetime(2019, 1, 1, 9, 0, 59)
    start_time_sub = datetime(2019, 1, 1, 9, 0, 20)
    end_time_sub = datetime(2019, 1, 1, 9, 0, 30)
    grid_geom = 'cart'
    with pytest.raises(Exception):
        AidaAccessorVDF._check_inputs(time_par, start_time, end_time,
                                      start_time_sub, end_time_sub,
                                      grid_geom)


def test_time_average():
    """Unit test on AidaAccessorVDF.time_average method."""
    time_v = np.arange(datetime(2019, 1, 1), datetime(2019, 1, 2),
                       timedelta(minutes=20)).astype(datetime)
    reso = time_v.size
    v = np.ones((3, reso))
    time_oi = np.arange(datetime(2019, 1, 1, 2), datetime(2019, 1, 1, 22),
                        timedelta(minutes=53)).astype(datetime)
    v_av = AidaAccessorVDF._time_average(v, time_v, time_oi)
    # Check shape.
    assert v_av.shape == (3, 23)
    # The binning+averaging should return precisely one in this case.
    assert np.allclose(v_av, 1.)


def test_time_sub_range():
    """Unit test on AidaAccessorVDF.time_sub_range method."""
    time_delta = timedelta(minutes=20)
    time_par = np.arange(datetime(2019, 1, 1), datetime(2019, 1, 2),
                         time_delta).astype(datetime)
    start_time_sub = datetime(2019, 1, 1, 10)
    end_time_sub = datetime(2019, 1, 1, 14)
    nb_vdf = time_par.size
    ind_dis_oi, ind_start, ind_stop = \
        AidaAccessorVDF._time_sub_range(nb_vdf, time_par,
                                       start_time_sub, end_time_sub)
    assert ind_dis_oi.size == int((end_time_sub - start_time_sub) / time_delta)
    assert isinstance(ind_start, np.int64)
    assert isinstance(ind_stop, np.int64)


def test_transform_grid():
    """Unit test on AidaAccessorVDF.transform_grid method."""
    reso = 5
    grid_cart = np.zeros((3, reso, reso, reso))
    grid_cart[0] = 1.
    frame = 'instrument'
    R_b_to_dbcs = np.eye(3)
    ibulkv_dbcs_par = np.zeros(3)
    grid_s = AidaAccessorVDF._transform_grid(grid_cart, R_b_to_dbcs,
                                             ibulkv_dbcs_par, frame)
    assert grid_s.shape == (3, reso, reso, reso)
    assert np.allclose(grid_s, vdfu.cart2spher(-1 * grid_cart))

    frame = 'B'
    grid_s = AidaAccessorVDF._transform_grid(grid_cart, R_b_to_dbcs,
                                             ibulkv_dbcs_par, frame)
    assert np.allclose(grid_s[0], 1.)
    assert np.allclose(grid_s[1], np.pi / 2.)
    assert np.allclose(grid_s[2], np.pi)


def test_interpolate_spher_mms_near(interpolate_inputs):
    """Unit test on AidaAccessorVDF.interpolate_spher_mms method.

    Nearest_neighbour interpolation."""
    vdf0, speed, theta, phi, reso, grid_s = interpolate_inputs
    interp_schem = 'near'
    d = AidaAccessorVDF._interpolate_spher_mms(vdf0, speed, theta, phi, grid_s,
                                               interp_schem)
    assert d.shape == (reso, reso, reso)
    assert np.allclose(d, 1.)


def test_interpolate_spher_mms_lin(interpolate_inputs):
    """Unit test on AidaAccessorVDF.interpolate_spher_mms method.

    Trilinear interpolation."""
    vdf0, speed, theta, phi, reso, grid_s = interpolate_inputs
    interp_schem = 'lin'
    d = AidaAccessorVDF._interpolate_spher_mms(vdf0, speed, theta, phi, grid_s,
                                               interp_schem)
    assert d.shape == (reso, reso, reso)
    assert np.allclose(d, 1.)


def test_interpolate_spher_mms_cub(interpolate_inputs):
    """Unit test on AidaAccessorVDF.interpolate_spher_mms method.

    Tricubic interpolation."""
    try:
        import tricubic
        tricubic_imported = True
    except ModuleNotFoundError:
        tricubic_imported = False
    if not tricubic_imported:
        pytest.skip('Unavailable Module.')

    vdf0, speed, theta, phi, reso, grid_s = interpolate_inputs
    interp_schem = 'cub'

    d = AidaAccessorVDF._interpolate_spher_mms(vdf0, speed, theta, phi, grid_s,
                                               interp_schem)
    assert d.shape == (reso, reso, reso)
    assert np.allclose(d, 1.)


@pytest.fixture(scope="module")
def interpolate_inputs():
    vdf0 = np.ones((32, 16, 32))
    speed = np.linspace(1., 1.e8, 32)
    theta = np.linspace(.01, .95 * np.pi, 16)
    phi = np.linspace(.01, 1.95 * np.pi, 32)
    reso = 5
    grid_s = np.zeros((3, reso, reso, reso))
    grid_s[0] = 1.
    grid_s[1] = np.pi / 2.

    return vdf0, speed, theta, phi, reso, grid_s
