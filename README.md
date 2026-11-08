# Pixel Art Character Generator

MacBook M2 Pro에서 로컬로 학습·추론하는 픽셀아트 캐릭터 생성 프로젝트입니다. [전체 기준 명세](docs/spec.md)는 이전 대화에서 작성한 v0.2.0 문서입니다.

V1 목표는 자연어 프롬프트·장르·테마를 조건으로 자체 Conditional Masked Pixel Transformer가 32×32 캐릭터를 만들고, 투명 배경 RGBA PNG로 내보내는 것입니다. 현재는 Phase 0 기반과 무조건부 Transformer 실험 코드만 있습니다. 생성 서비스나 완성된 조건부 모델은 아직 없습니다.

## 개발 환경

Python 3.11–3.13, uv를 사용합니다.

```sh
uv sync --extra dev --python 3.13
uv run pytest
uv run ruff check .
```

[초기화 기록](docs/implementation.md)과 [Phase 1 계획](docs/phase1.md)을 참고하세요. Teacher–Student와 GAN은 후속 연구 단계입니다.
