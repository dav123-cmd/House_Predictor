"""
Loads the trained FeedForwardRegressor + scaler once (singleton) and
exposes predict_price() for Django views to call.
"""
import os
import threading
import numpy as np
import torch
import joblib

from .network import FeedForwardRegressor

_lock = threading.Lock()
_model = None
_scaler_bundle = None

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), 'artifacts')
MODEL_PATH = os.path.join(ARTIFACT_DIR, 'price_model.pth')
SCALER_PATH = os.path.join(ARTIFACT_DIR, 'scaler.pkl')


def _load():
    global _model, _scaler_bundle
    with _lock:
        if _model is None:
            if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
                raise FileNotFoundError(
                    "Model artifacts not found. Run `python pricing/ml/train.py` first "
                    "to train and save the model."
                )
            model = FeedForwardRegressor()
            model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
            model.eval()
            _model = model
            _scaler_bundle = joblib.load(SCALER_PATH)
    return _model, _scaler_bundle


def predict_price(area: float, bedrooms: float, bathrooms: float,
                   age: float, location_score: float) -> float:
    """Run the trained feed-forward network and return the predicted price."""
    model, bundle = _load()
    scaler = bundle['feature_scaler']
    y_mean, y_std = bundle['y_mean'], bundle['y_std']

    X = np.array([[area, bedrooms, bathrooms, age, location_score]], dtype=np.float32)
    X_scaled = scaler.transform(X)
    X_tensor = torch.tensor(X_scaled, dtype=torch.float32)

    with torch.no_grad():
        pred_scaled = model(X_tensor).item()

    price = pred_scaled * y_std + y_mean
    return max(price, 0.0)
