import numpy as np
import xarray as xr
import pandas as pd
from aidapy.aidaxr import graphical
import pytest

@pytest.mark.skip(reason="Not relevant")
@pytest.mark.parametrize("col,row", [
    (14, 3),
    (30, 3),
    (50, 3),
])
def test_peek(col, row):
    np.random.seed(0)
    data = np.random.rand(col, row)
    locs = ['IA', 'IL', 'IN']
    time = pd.date_range('2000-01-01', periods=col)
    foo = xr.DataArray(data, coords=[time, locs], dims=['time', 'space'], attrs={'units': 'meters'})
    foo.graphical.peek()


@pytest.mark.skip(reason="Not relevant")
@pytest.mark.parametrize("col,row,col1,row1", [
    (14, 3, 30, 3),
    (30, 3, 10, 3),
    (50, 3, 80, 3),
])
def test_peek_dataset(col, row, col1, row1):
    np.random.seed(0)
    data = np.random.rand(col, row)
    locs = ['IA', 'IL', 'IN']
    time = pd.date_range('2000-01-01', periods=col)
    foo = xr.DataArray(data, coords=[time, locs], dims=['time', 'space'], attrs={'units': 'meters'})

    data2 = np.random.rand(col1, row1)
    time2 = pd.date_range('2000-01-01', periods=col1)
    foo2 = xr.DataArray(data2, coords=[time2, locs], dims=['time2', 'space'], attrs={'units': 'meters'})

    ds = xr.Dataset({'foo1': foo, 'foo2': foo2})
    ds.graphical.peek()
