"""Adapter that lets any scikit-learn regressor satisfy the ``Forecaster`` contract.

Imported explicitly (``from mlt.models.sklearn_wrap import SklearnForecaster``) so that the rest
of the package does not need scikit-learn. State is a base64 pickle: enough for research and for
resuming a run; the production format is decided by ADR 0001.
"""
from __future__ import annotations

import base64
import pickle
from collections.abc import Callable

import numpy as np

from .base import Forecaster


class SklearnForecaster(Forecaster):
    def __init__(self, factory: Callable[[], object]) -> None:
        self.estimator = factory()

    def fit(self, X: np.ndarray, y: np.ndarray) -> SklearnForecaster:
        self.estimator.fit(np.asarray(X, dtype=float), np.asarray(y, dtype=float))
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        return np.asarray(self.estimator.predict(np.atleast_2d(np.asarray(x, dtype=float))), dtype=float)

    def get_state(self) -> dict:
        return {"estimator": base64.b64encode(pickle.dumps(self.estimator)).decode("ascii")}

    def set_state(self, state: dict) -> None:
        self.estimator = pickle.loads(base64.b64decode(state["estimator"]))
