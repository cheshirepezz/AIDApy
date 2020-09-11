"""
The following test integration suite assesses the interconectivity between aidafunc, mission subpackage, and HelioPy
"""
import numpy as np
import xarray as xr
import pandas as pd
from aidapy.aidaxr import statistics
import pytest

## Test xr.DataArray

@pytest.mark.parametrize("col,row,scale,order", [
    (10, 3, [2, 4], 3)
])

def test_sfunc(col, row, scale, order):
    np.random.seed(0)
    data = np.random.rand(col, row)
    locs = ['IA', 'IL', 'IN']
    time = pd.date_range('2000-01-01', periods=col)
    foo = xr.DataArray(data, coords=[time, locs], dims=['time', 'space'], attrs={'units': 'meters'})
    y = foo.statistics.sfunc(scale=scale, order=order)
    target = np.array([[0.08681352, 0.07663991, 0.27091121],
                      [0.15481142, 0.04342448, 0.04102923]])

    assert np.allclose(y.values, target)

def test_sfunc_xrdataset():
    np.random.seed(0)
    time = pd.date_range('2000-01-01', freq='H', periods=365 * 24)
    data = np.random.rand(10, 3)
    locs = ['IA', 'IL', 'IN']
    time = pd.date_range('2000-01-01', periods=10)
    foo = xr.DataArray(data, coords=[time, locs], dims=['time', 'space'], attrs={'units': 'meters'})
    #convert xr.DataArray to xr.Dataset
    foo_dataset = foo.to_dataset(name='test')
    y = foo_dataset.statistics.sfunc(scale=[2, 4], order=3)
    target = np.array([[0.08681352, 0.07663991, 0.27091121],
                       [0.15481142, 0.04342448, 0.04102923]])

    assert np.allclose(y[('test')].values, target)


@pytest.mark.parametrize("col,row,scale,order", [
    (14, 3, [3], 3),
    (30, 3, [2], 3),
    (50, 3, [2, 5], 3),
])
def test_sfunc_multi(col, row, scale, order):
    np.random.seed(0)
    data = np.random.rand(col, row)
    locs = ['IA', 'IL', 'IN']
    time = pd.date_range('2000-01-01', periods=col)

    foo = xr.DataArray(data, coords=[time, locs], dims=['time', 'space'], attrs={'units': 'meters'})
    y = foo.statistics.sfunc(scale=scale, order=order)
    assert isinstance(y, xr.DataArray)

def test_psd():
    fs = 2**13
    N = 2**13
    amp = 2*np.sqrt(2)
    freq = 2.**10
    t = np.arange(N) / fs
    x = amp*np.array([np.sin(2*np.pi*freq*t), np.cos(2*np.pi*freq*t)] ).T
    tcoords = pd.date_range('2000-01-01', freq='s', periods=N)
    obscoords = ['sin', 'cos']
    data = xr.DataArray(data=x, dims=['time','observations'], coords=[tcoords, obscoords])
    y = data.statistics.psd(fs=fs, nperseg=2**8)
    f = y.where(y==y.max(axis=0), drop=True).coords['frequency'].values
    assert(freq==f[0])

def test_psdwt():
    from scipy import signal
    import matplotlib.pyplot as plt
    N = 200
    nscales = 20
    widths = np.arange(1, nscales+1)
    t = np.linspace(-1, 1, N, endpoint=False)
    sig = np.zeros(N)
    sig[100] = 1.0
    tcoords = pd.date_range('2000-01-01', freq='s', periods=N)
    obscoords = ['signal']
    data = xr.DataArray(data=sig, coords=[tcoords], dims=['time'])
    y = data.statistics.psdwt(signal.gaussian, widths)
    maxloc = np.unravel_index(y.argmax(), y.shape)
    assert(np.isclose(y.max(),1,rtol=1e-3))
    assert(int(N/2)==maxloc[0])
    assert(nscales-1==maxloc[1])

@pytest.mark.parametrize("col,row", [
    (14, 3),
    (30, 3),
    (50, 3),
])
def test_psd_multi(col, row):
    np.random.seed(0)
    data = np.random.rand(col, row)
    locs = ['IA', 'IL', 'IN']
    time = pd.date_range('2000-01-01', periods=col)
    foo = xr.DataArray(data, coords=[time, locs], dims=['time', 'space'], attrs={'units': 'meters'})
    y = foo.statistics.psd(scaling='density')
    assert isinstance(y, xr.DataArray)


def test_mean():
    np.random.seed(0)
    data = np.random.rand(10, 3)
    locs = ['IA', 'IL', 'IN']
    time = pd.date_range('2000-01-01', periods=10)
    foo = xr.DataArray(data, coords=[time, locs], dims=['time', 'space'], attrs={'units': 'meters'})
    y = foo.statistics.mean(time=2, center=True)
    target = np.array([[0.546848, 0.569422, 0.624329],
                       [0.491235, 0.657714, 0.804778],
                       [0.410514, 0.841749, 0.746279],
                       [0.475743, 0.858661, 0.299965],
                       [0.327587, 0.472908, 0.451828],
                       [0.432643, 0.445115, 0.905619],
                       [0.788658, 0.665746, 0.879574],
                       [0.458716, 0.5507  , 0.461941],
                       [0.531472, 0.580885, 0.279008]])

    assert np.allclose(y.values[1:, :], target)


def test_std():
    np.random.seed(0)
    data = np.random.rand(10, 3)
    locs = ['IA', 'IL', 'IN']
    time = pd.date_range('2000-01-01', periods=10)
    foo = xr.DataArray(data, coords=[time, locs], dims=['time', 'space'], attrs={'units': 'meters'})
    y = foo.statistics.std(time=3, center=True)

    target = np.array([[0.051531, 0.19302 , 0.16093 ],
                       [0.067088, 0.201279, 0.183693],
                       [0.077481, 0.056838, 0.364454],
                       [0.198091, 0.399006, 0.313031],
                       [0.289241, 0.41432 , 0.397916],
                       [0.330815, 0.347013, 0.083844],
                       [0.316138, 0.167227, 0.356355],
                       [0.360201, 0.074107, 0.261079]])

    assert np.allclose(y.values[1:-1, :], target)

