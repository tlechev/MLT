"""Causal walk-forward training for batch models (the batch counterpart of ``run_online``).

At a retrain point ``r`` (the close of bar ``r``) the model is fitted on the rows whose target is
already known, i.e. rows ``i <= r - horizon`` (their target reaches ``close[i + horizon]``, not
later than ``close[r]``). It then predicts rows ``r .. r + retrain_every - 1`` without being
refitted. Rows near ``r`` whose targets are not yet known are never used for training, which is
the purge of ADR 0004 applied at every retrain.
"""
from __future__ import annotations

from collections.abc import Callable

import numpy as np

from .base import Forecaster


def walk_forward(
    make_model: Callable[[], Forecaster],
    X: np.ndarray,
    y: np.ndarray,
    horizon: int,
    first_pred: int,
    retrain_every: int = 168,
    min_train: int = 500,
    stop: int | None = None,
) -> np.ndarray:
    """One prediction per row in ``[first_pred, stop)``; NaN elsewhere or where a row is not finite."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(X)
    stop = n if stop is None else min(stop, n)
    finite_x = np.isfinite(X).all(axis=1)
    preds = np.full(n, np.nan)
    r = first_pred
    while r < stop:
        end = min(r + retrain_every, stop)
        train = (np.arange(n) <= r - horizon) & finite_x & np.isfinite(y)
        if train.sum() >= min_train:
            model = make_model()
            model.fit(X[train], y[train])
            rows = np.arange(r, end)
            rows = rows[finite_x[rows]]
            if len(rows):
                preds[rows] = model.predict(X[rows])
        r = end
    return preds
