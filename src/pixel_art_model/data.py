"""Palette-indexed image validation for the fixed-grid model."""

from pathlib import Path

import torch
from PIL import Image
from torch import Tensor


def load_indexed_image(path: str | Path, image_size: int, palette_size: int) -> Tensor:
    """Load a square P-mode PNG without resampling or changing palette indices."""
    with Image.open(path) as image:
        if image.format != "PNG" or image.mode != "P":
            raise ValueError("expected a palette-indexed PNG (P mode)")
        if image.size != (image_size, image_size):
            raise ValueError(f"expected {image_size}x{image_size} image")
        pixels = torch.tensor(list(image.get_flattened_data()), dtype=torch.long)
    if torch.any(pixels >= palette_size):
        raise ValueError("pixel index exceeds configured palette size")
    return pixels
