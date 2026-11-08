import pytest
import torch
from PIL import Image

from pixel_art_model.data import load_indexed_image
from pixel_art_model.model import MaskedPixelTransformer, ModelConfig


def test_forward_and_masked_training_step():
    model = MaskedPixelTransformer(ModelConfig(image_size=4, palette_size=4, hidden_size=16, layers=1, heads=4))
    pixels = torch.randint(0, 4, (2, 16))
    mask = torch.zeros_like(pixels, dtype=torch.bool)
    mask[:, ::2] = True
    assert model(pixels).shape == (2, 16, 4)
    loss = model.masked_loss(pixels, mask)
    assert torch.isfinite(loss)
    loss.backward()
    assert model.head.weight.grad is not None


def test_indexed_png_validation(tmp_path):
    path = tmp_path / "sprite.png"
    image = Image.new("P", (4, 4), 2)
    image.save(path)
    assert load_indexed_image(path, 4, 4).shape == (16,)
    with pytest.raises(ValueError, match="expected 8x8"):
        load_indexed_image(path, 8, 4)
