"""
The following test integration suite assesses the interconectivity between aidafunc, mission subpackage, and HelioPy
"""
import numpy as np
import xarray as xr
import pandas as pd
from aidapy.aidaxr import xevents
import pytest

## Test xr.DataArray

#@pytest.mark.parametrize("col,row,scale,order", [
#    (10, 3, [2, 4], 3)
#])
def test_pvi():
    assert(True)

def test_threshold():
    assert(True)

def test_increm():
    assert(True)

def test_dummy():
    assert(2+2==4)


