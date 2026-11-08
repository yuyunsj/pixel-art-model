# Repository guidance

- `docs/spec.md` v0.2.0 is the source of truth. Read it before changing scope or architecture.
- Follow the roadmap: Phase 1 pixel representation, Phase 2 conditional model and sampling, Phase 3 training, Phase 4 local service. Teacher–Student and GAN belong to Phases 5 and 6.
- Implement the core Pixel Transformer directly in PyTorch. Do not replace it with a complete external generator.
- Preserve 32×32 V1 pixels, a 32-color palette plus transparency, and RGBA PNG output. Do not silently resize or interpolate sprites.
- Keep data, model, training, inference, and service components independently testable.
- Track dataset source, license, and character ID. Do not commit datasets or checkpoints.
- Document unresolved choices and alternatives before fixing them.
- Validate with `uv run pytest` and `uv run ruff check .`.
