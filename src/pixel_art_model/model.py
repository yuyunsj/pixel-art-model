"""A minimal, directly implemented masked token transformer for indexed pixels."""

from dataclasses import dataclass

import torch
from torch import Tensor, nn


@dataclass(frozen=True)
class ModelConfig:
    image_size: int = 32
    palette_size: int = 33
    hidden_size: int = 192
    layers: int = 4
    heads: int = 4

    def __post_init__(self) -> None:
        if self.image_size < 1 or self.palette_size < 2:
            raise ValueError("image_size must be positive and palette_size >= 2")
        if self.hidden_size < 1 or self.layers < 1 or self.heads < 1:
            raise ValueError("hidden_size, layers, and heads must be positive")
        if self.hidden_size % self.heads:
            raise ValueError("hidden_size must be divisible by heads")


class MaskedPixelTransformer(nn.Module):
    """Predict palette indices at masked locations in a fixed square image."""

    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self.config = config
        count = config.image_size**2
        self.mask_token_id = config.palette_size
        self.token_embedding = nn.Embedding(config.palette_size + 1, config.hidden_size)
        self.position_embedding = nn.Embedding(count, config.hidden_size)
        block = nn.TransformerEncoderLayer(
            d_model=config.hidden_size,
            nhead=config.heads,
            dim_feedforward=config.hidden_size * 4,
            batch_first=True,
            norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(block, num_layers=config.layers)
        self.norm = nn.LayerNorm(config.hidden_size)
        self.head = nn.Linear(config.hidden_size, config.palette_size)

    def forward(self, tokens: Tensor) -> Tensor:
        count = self.config.image_size**2
        if tokens.ndim != 2 or tokens.shape[1] != count:
            raise ValueError(f"expected tokens of shape [batch, {count}]")
        if tokens.dtype != torch.long:
            raise TypeError("tokens must be torch.long palette indices")
        if torch.any(tokens < 0) or torch.any(tokens > self.mask_token_id):
            raise ValueError("token index outside palette or mask token")
        positions = torch.arange(count, device=tokens.device)
        hidden = self.token_embedding(tokens) + self.position_embedding(positions)
        return self.head(self.norm(self.transformer(hidden)))

    def masked_loss(self, original: Tensor, mask: Tensor) -> Tensor:
        """Cross entropy only on masked pixels; requires at least one masked pixel."""
        if original.ndim != 2 or mask.shape != original.shape or mask.dtype != torch.bool:
            raise ValueError("original and boolean mask must have matching [batch, pixels] shape")
        if not torch.any(mask):
            raise ValueError("mask must select at least one pixel")
        if torch.any(original < 0) or torch.any(original >= self.config.palette_size):
            raise ValueError("original pixel outside palette")
        masked = original.masked_fill(mask, self.mask_token_id)
        logits = self(masked)
        return nn.functional.cross_entropy(logits[mask], original[mask])
