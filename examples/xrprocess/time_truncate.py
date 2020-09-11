import xarray as xr
import datetime
import pandas as pd
import numpy as np

time = pd.date_range('2000-01-01', freq='H', periods=365 * 24)
ds = xr.Dataset({'foo': ('time', np.arange(365 * 24)), 'time': time})
print(ds)

ds2 = ds.sel(time=slice('2000-06-01', '2000-06-10'))
print(ds2)
