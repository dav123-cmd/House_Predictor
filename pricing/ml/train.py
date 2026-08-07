"""
Training script for the price-prediction Feed-Forward Neural Network.

Run manually:
    python pricing/ml/train.py

It will:
  1. Generate a synthetic-but-realistic housing dataset (replace this
     with pandas.read_csv(...) on your real dataset if you have one).
  2. Standardize features with sklearn's StandardScaler.
  3. Train the FeedForwardRegressor from network.py using MSE loss + Adam.
  4. Save the trained weights and the fitted scaler into pricing/ml/artifacts/
     so the Django app can load them at request time.
"""
import os
import sys
import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

sys.path.append(os.path.dirname(__file__))
from network import FeedForwardRegressor

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), 'artifacts')
os.makedirs(ARTIFACT_DIR, exist_ok=True)

MODEL_PATH = os.path.join(ARTIFACT_DIR, 'price_model.pth')
SCALER_PATH = os.path.join(ARTIFACT_DIR, 'scaler.pkl')


def generate_synthetic_data(n_samples: int = 5000, seed: int = 42):
    """Synthetic housing dataset: area, bedrooms, bathrooms, age, location_score -> price."""
    rng = np.random.default_rng(seed)

    area = rng.uniform(400, 4500, n_samples)                 # sq ft
    bedrooms = rng.integers(1, 6, n_samples).astype(float)    # 1-5
    bathrooms = rng.integers(1, 4, n_samples).astype(float)   # 1-3
    age = rng.uniform(0, 40, n_samples)                       # years
    location_score = rng.uniform(1, 10, n_samples)            # 1 (poor) - 10 (prime)

    noise = rng.normal(0, 12000, n_samples)

    price = (
        area * 320
        + bedrooms * 14000
        + bathrooms * 9000
        - age * 650
        + location_score * 9500
        + 15000
        + noise
    )
    price = np.clip(price, 20000, None)

    X = np.column_stack([area, bedrooms, bathrooms, age, location_score])
    y = price.reshape(-1, 1)
    return X.astype(np.float32), y.astype(np.float32)


def train():
    X, y = generate_synthetic_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Scale target too (helps training stability), we invert at prediction time
    y_mean, y_std = y_train.mean(), y_train.std()
    y_train_scaled = (y_train - y_mean) / y_std
    y_test_scaled = (y_test - y_mean) / y_std

    X_train_t = torch.tensor(X_train_scaled, dtype=torch.float32)
    y_train_t = torch.tensor(y_train_scaled, dtype=torch.float32)
    X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)
    y_test_t = torch.tensor(y_test_scaled, dtype=torch.float32)

    model = FeedForwardRegressor(input_dim=X.shape[1])
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    epochs = 200
    batch_size = 64
    n = X_train_t.shape[0]

    for epoch in range(1, epochs + 1):
        model.train()
        permutation = torch.randperm(n)
        epoch_loss = 0.0
        for i in range(0, n, batch_size):
            idx = permutation[i:i + batch_size]
            xb, yb = X_train_t[idx], y_train_t[idx]

            optimizer.zero_grad()
            preds = model(xb)
            loss = criterion(preds, yb)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * xb.size(0)

        if epoch % 20 == 0 or epoch == 1:
            model.eval()
            with torch.no_grad():
                test_preds = model(X_test_t)
                test_loss = criterion(test_preds, y_test_t).item()
            print(f"Epoch {epoch:4d} | train_loss={epoch_loss / n:.5f} | test_loss={test_loss:.5f}")

    # Save model weights + scaler + target normalization stats
    torch.save(model.state_dict(), MODEL_PATH)
    joblib.dump(
        {'feature_scaler': scaler, 'y_mean': float(y_mean), 'y_std': float(y_std)},
        SCALER_PATH,
    )
    print(f"\nSaved model to {MODEL_PATH}")
    print(f"Saved scaler to {SCALER_PATH}")


if __name__ == '__main__':
    train()
