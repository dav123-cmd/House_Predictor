"""
Feed-Forward Neural Network for Price Regression.

Architecture:
    Input (5 features) -> Dense(64) -> ReLU -> Dense(32) -> ReLU
    -> Dense(16) -> ReLU -> Dense(1) [predicted price]

This is a standard fully-connected feed-forward regressor: every layer
feeds forward into the next with no recurrence/attention, ending in a
single linear output neuron suitable for continuous price prediction.
"""
import torch
import torch.nn as nn

INPUT_FEATURES = 5  # area, bedrooms, bathrooms, age, location_score


class FeedForwardRegressor(nn.Module):
    def __init__(self, input_dim: int = INPUT_FEATURES):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
