import numpy as np
import pytest

from mlt.models.linear import OnlineLinear
from mlt.models.sklearn_wrap import SklearnForecaster
from mlt.models.walkforward import walk_forward


class MeanModel(OnlineLinear):
    """Predicts the mean of the targets it was fitted on (makes leakage easy to see)."""

    def __init__(self):
        super().__init__(1)
        self.mean = 0.0

    def fit(self, X, y):
        self.mean = float(np.mean(y))
        return self

    def predict(self, x):
        return np.full(len(np.atleast_2d(x)), self.mean)


def data(n=400, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, 2)), rng.normal(size=n)


def test_prediction_never_uses_targets_that_are_not_yet_known():
    X, y = data()
    horizon, r, every = 20, 200, 50
    base = walk_forward(MeanModel, X, y, horizon, first_pred=r, retrain_every=every, min_train=10)
    y2 = y.copy()
    y2[r - horizon + 1:] += 1000.0          # targets that are NOT matured at the retrain point r
    other = walk_forward(MeanModel, X, y2, horizon, first_pred=r, retrain_every=every, min_train=10)
    assert np.allclose(other[r : r + every], base[r : r + every])      # same model for the first interval
    assert not np.allclose(other[r + every : r + 2 * every], base[r + every : r + 2 * every])


def test_model_is_refitted_only_at_the_retrain_points():
    X, y = data()
    fits = []

    def factory():
        m = MeanModel()
        fits.append(m)
        return m

    preds = walk_forward(factory, X, y, horizon=5, first_pred=100, retrain_every=100, min_train=10, stop=350)
    assert len(fits) == 3                                    # r = 100, 200, 300
    assert np.isnan(preds[:100]).all() and np.isnan(preds[350:]).all()
    assert len(np.unique(preds[100:200])) == 1               # one model per interval


def test_waits_for_enough_training_rows_and_skips_non_finite_rows():
    X, y = data()
    X[150] = np.nan
    preds = walk_forward(MeanModel, X, y, horizon=5, first_pred=10, retrain_every=50, min_train=100)
    assert np.isnan(preds[:105]).all()                      # not enough matured rows before that
    assert np.isnan(preds[150]) and np.isfinite(preds[151])


def test_sklearn_adapter_fits_predicts_and_roundtrips_state():
    from sklearn.linear_model import Ridge

    rng = np.random.default_rng(1)
    X = rng.normal(size=(300, 3))
    y = X @ np.array([0.4, -0.2, 0.1])
    m = SklearnForecaster(lambda: Ridge(alpha=1e-6)).fit(X, y)
    assert m.predict(X[:5]) == pytest.approx(y[:5], abs=1e-3)
    n = SklearnForecaster(lambda: Ridge())
    n.set_state(m.get_state())
    assert n.predict(X[:5]) == pytest.approx(m.predict(X[:5]))
