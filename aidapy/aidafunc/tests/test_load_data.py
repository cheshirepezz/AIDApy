import pytest
import datetime
import numpy as np
import pandas as pd
import xarray as xr
from aidapy.aidafunc.load_data import load_data, _convert_dict_to_ds, \
    _rename_time_index, _check_all_dim

missions = ['omni', 'mms', 'cluster']


def test_bad_mission():
    start_time = datetime.datetime(2008, 1, 1, 0, 0, 0)
    end_time = datetime.datetime(2008, 1, 2, 0, 0, 0)
    settings = {}
    with pytest.raises(ValueError):
        load_data(mission='toto', start_time=start_time,
                  end_time=end_time, **settings)


@pytest.mark.parametrize("mission", missions)
def test_decreasing_start_end_time(mission):
    with pytest.raises(ValueError) as type_info:
        t_start = datetime.datetime(2014, 2, 1, 0, 0, 0)
        t_end = datetime.datetime(2014, 1, 31, 0, 0, 0)
        load_data(mission, t_start, t_end)


@pytest.mark.parametrize("mission", missions)
def test_bad_product(mission):
    start_time = datetime.datetime(2008, 1, 1, 0, 0, 0)
    end_time = datetime.datetime(2008, 1, 2, 0, 0, 0)
    settings = {'prod': ['toto_27']}
    with pytest.raises(ValueError):
        load_data(mission=mission, start_time=start_time,
                  end_time=end_time, **settings)


@pytest.fixture(scope="module")
def generate_dict_da():
    data1 = np.arange(30).reshape((-1, 3))
    locs1 = ['IA', 'IL', 'IN']
    time1 = pd.date_range('2000-01-01', periods=10)
    da1 = xr.DataArray(data1, coords=[time1, locs1], dims=['time', 'space1'],
                       attrs={'units': 'meters'})

    data2 = np.ones((4, 2))
    locs2 = ['x', 'y']
    time2 = pd.date_range('1994-01-01', periods=4)
    da2 = xr.DataArray(data2, coords=[time2, locs2], dims=['time', 'space2'],
                       attrs={'units': 'kg'})

    dict_da = {'da1': da1, 'da2': da2}
    return dict_da


def test_convert_dict_to_ds(generate_dict_da):
    dict_da = generate_dict_da
    xr_ds = _convert_dict_to_ds(dict_da, {'mission': 'test'})
    assert isinstance(xr_ds, xr.Dataset)


def test_rename_time_index(generate_dict_da):
    dict_da = generate_dict_da
    renamed_dict_da = _rename_time_index(dict_da)
    assert ('time1' in renamed_dict_da['da1'].dims)


def test_check_all_dim(generate_dict_da):
    dict_da = generate_dict_da
    with pytest.raises(ValueError):
        assert _check_all_dim(dict_da)
