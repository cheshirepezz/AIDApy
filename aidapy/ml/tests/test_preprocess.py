from aidapy.ml import preprocess
import numpy as np


def test_preprocess():
    histsize = 2
    forecast_time = 1

    X0 = np.linspace(1, 4, 4, dtype=int)[:, None]
    y0 = 2 * X0

    X, y, mask = preprocess.time_series(X0, y0, histsize, forecast_time)

    Xtrue = np.array([[1, 2], [2, 3]])
    ytrue = np.array([[2 * 3], [2 * 4]])
    assert np.all(X == Xtrue) and np.all(y == ytrue)
