import numpy as np


def time_series(X_in, y_in, histsize=1, forecast_offset=0, dropna=True, predict_change=False):
    """Preprocess time series data for machine learning purposes

    Create new features X containing a history of the old features, and define
    the targets at a future time defined by forecast_offset.

    :param X_in: input features (2D array)
    :param y_in: input targets (1D or 2D array)
    :param histsize: how much history to include
    :param forecast_offset: index offset of the forecast
    :param dropna: remove entries with missing values
    :param predict_change: if true, predict change in y (y[t+dt]-y[t])
    :returns: X, y, mask
    :rtype: preprocessed features X and targets y, and the corresponding mask

    """
    assert len(X_in) == len(y_in), "X_in and y_in should have the same length"
    assert X_in.ndim == 2, "X_in should be two-dimensional"

    X = np.full([X_in.shape[0], histsize * X_in.shape[1]], np.nan)
    y = np.full_like(y_in, np.nan)

    # Fill the range where all X and y values are defined, so exclude the
    # beginning and end
    for i in range(histsize-1, X_in.shape[0]-forecast_offset):
        X[i] = X_in[i-histsize+1:i+1].flatten()
        if predict_change:
            y[i] = y_in[i+forecast_offset] - y_in[i]
        else:
            y[i] = y_in[i+forecast_offset]

    # Filter any entries with a NaN
    mask = np.ones(len(X), dtype=bool)
    if dropna and y.ndim == 1:
        mask = ~(np.any(np.isnan(X), axis=1) | np.isnan(y))
    if dropna and y.ndim == 2:
        mask = ~(np.any(np.isnan(X), axis=1) | np.any(np.isnan(y), axis=1))

    return X[mask], y[mask], mask
