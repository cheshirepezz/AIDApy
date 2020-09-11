import pytest
from aidapy.ml import mlp
NeuralNetRegressor = pytest.importorskip("skroch.NeuralNetRegressor")
torch = pytest.importorskip("torch")
import numpy as np

def test_mlp_creation():
    mlp_model = NeuralNetRegressor(
        mlp.RegressorMlp,
        max_epochs=25,
        lr=0.001,
        batch_size=128,
        optimizer=torch.optim.Adam,
        module__layer_sizes=[16, 64, 64, 64, 1]
    )
    assert mlp_model is not None

def test_mlp_linear_model():
    mlp_model = NeuralNetRegressor(
        mlp.RegressorMlp,
        max_epochs=100,
        lr=0.1,
        batch_size=1,
        optimizer=torch.optim.Adam,
        module__layer_sizes=[1, 1],
        module__afunc=None
    )

    X = np.linspace(0., 1., 10)[:, None]
    y = X - 0.5
    mlp_model.fit(X, y)
    y_pred = mlp_model.predict(X)
    mean_abs_error = np.mean(np.abs(y-y_pred))
    assert mean_abs_error < 0.15
