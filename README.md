# PricePredict AI — Django + PyTorch Price Prediction App

## What this project is

A web application that predicts a **property price** from a small set of
inputs (area, bedrooms, bathrooms, age, location score) using a **Feed-Forward
Neural Network regression model** built in **PyTorch**, served through a
**Django** backend, with an HTML/Bootstrap **frontend template**.

It's a template you can adapt to any pricing problem (real estate, used cars,
insurance premiums, product pricing, etc.) — just swap the input features and
retrain.

## How it works end-to-end

1. **User** fills in a form on the Django-rendered HTML page (area, bedrooms,
   bathrooms, age, location score).
2. **Django view** (`pricing/views.py`) validates the form and calls the
   PyTorch inference function.
3. **PyTorch model** (`pricing/ml/network.py` — a `FeedForwardRegressor`)
   loads its trained weights and predicts a single continuous value: price.
4. The prediction is **saved to the database** (`PredictionHistory` model)
   and shown back to the user, along with a small history table.

## Model architecture (Feed-Forward Regression)

```
Input(5 features) -> Dense(64) -> ReLU -> Dropout(0.1)
                   -> Dense(32) -> ReLU
                   -> Dense(16) -> ReLU
                   -> Dense(1)  [predicted price]
```

- Loss: MSELoss
- Optimizer: Adam (lr=1e-3)
- Features and target are standardized with `StandardScaler` before training
  (scaler is saved alongside model weights so inference uses the same
  transformation).

## Project structure

```
home_price_predictor/
├── manage.py
├── requirements.txt
├── home_price_predictor/        # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
└── pricing/                     # Django app
    ├── models.py                # PredictionHistory (DB record of predictions)
    ├── forms.py                 # PricingForm (user input validation)
    ├── views.py                 # Glue between form <-> PyTorch model
    ├── urls.py
    ├── admin.py
    ├── templates/pricing/home.html   # Frontend (Bootstrap UI)
    └── ml/
        ├── network.py            # FeedForwardRegressor (PyTorch nn.Module)
        ├── train.py               # Training script (run this first)
        ├── predictor.py           # Loads trained model, exposes predict_price()
        └── artifacts/             # price_model.pth + scaler.pkl saved here
```

## Setup & run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the PyTorch model (creates pricing/ml/artifacts/*)
python pricing/ml/train.py

# 3. Set up the Django database
python manage.py migrate

# 4. Run the dev server
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser.

## Using your own real dataset

`pricing/ml/train.py` currently generates a synthetic dataset so the project
runs immediately with no external data. To use real data:

1. Replace `generate_synthetic_data()` with a `pandas.read_csv('your_data.csv')`
   call, extracting the same 5 feature columns (or update
   `INPUT_FEATURES` in `network.py` if you add/remove features — and update
   `PricingForm` + the template to match).
2. Re-run `python pricing/ml/train.py`.
3. Restart the Django server — `predictor.py` will pick up the new weights.

## Notes

- `PredictionHistory` in `models.py` persists every prediction to SQLite so
  you get a simple audit trail / dataset of predictions over time.
- The model loads once (singleton pattern in `predictor.py`), not on every
  request, so inference is fast.
