# 초기화 기록과 원본 명세 대조

이 문서는 [spec.md](spec.md) v0.2.0을 기준으로 한다. 이전에 작업 지시문만을 명세로 오인해 만든 초기 구현을 대조하여 기록한다.

| 단계 | 현재 구현·결정 | 검증 | 다음 작업 |
| --- | --- | --- | --- |
| 1. 구조·스택 | Python 3.13, PyTorch, Pillow, uv, pytest, Ruff를 구성했다. 모델·데이터 코드를 분리했다. | 패키지 설치 및 import 성공 | 명세의 `src/pixelgen` 계층, 조건 인코더와 서비스 경계 설계 |
| 2. 문서 | README, AGENTS, 기준 명세를 작성했다. 원본 대화의 전체 v0.2.0 명세로 교체했다. | 명세의 V1/Phase 정의 확인 | architecture, tech-stack, roadmap 세부 문서 |
| 3. 환경 | `pyproject.toml`, `uv.lock`, 가상환경, Git 저장소를 구성했다. | `uv sync --extra dev` 성공 | MPS/CPU 실행 검증, 향후 단계별 의존성 추가 |
| 4. Phase 0 | 최소 패키지, P 모드 PNG 검증, 무조건부 Masked Pixel Transformer 실험 코드를 마련했다. 모델 코드는 원래 Phase 2 작업의 선행 프로토타입이다. 기본 설정은 32×32, 33개 출력 토큰(32색+투명), 192차원, 4층, 4헤드다. | pytest 2개 통과, Ruff 통과 | 설정 관리, 2D 위치 인코딩, 조건부 입력은 Phase 2에서 구현 |
| 5. Phase 1 | [phase1.md](phase1.md)에 팔레트·토큰화·복원 계획을 정리했다. | 명세 완료 조건과 대조 | RGBA 왕복 변환 구현 |

## 설계 차이와 대안

- 현 모델은 1D 위치 임베딩과 무조건부 복원을 사용한다. 원본 명세는 2D 위치 인코딩과 Prompt/Genre/Theme 조건을 요구한다. Phase 0 범위 밖의 모델 프로토타입으로 유지하고, Phase 2에서 조건부 모델로 확장한다. 즉 V1 생성 모델 완성으로 간주하지 않는다.
- 입력 검증은 현재 P 모드 PNG만 받는다. 원본 명세의 최종 입력/출력은 RGBA다. 기존 검증기는 간단한 중간 형식으로만 유지하고 Phase 1에서 RGBA 변환을 정식 구현한다.
- 원본 명세 권장 구조는 `src/pixelgen`이다. 현재 `src/pixel_art_model`은 이미 설치·검증된 최소 패키지다. Phase 1 시작 전에 이름을 일괄 변경하거나 현 이름으로 확장하는 두 선택지가 있다. 불필요한 두 패키지 공존은 피한다.
- 투명 토큰의 정식 ID, 팔레트 RGB 값, 알파 처리, 양자화 방법은 명세에서 구체화되지 않았다. Phase 1에서 명시적으로 결정한다.
- Teacher–Student와 GAN은 각각 Phase 5·6의 선택적 연구 단계이며 현재 구현하지 않는다. 관련 라이선스는 실제 후보를 정할 때 확인한다.

## 테스트 기록

Python 3.13에서 `uv sync --extra dev`, `uv run pytest -q`(2개 통과), `uv run ruff check .`(통과). PyTorch의 선택적 NumPy 통합 미설치 및 nested tensor 최적화 경고가 있었다. 실제 MPS 학습, 조건부 생성, RGBA 왕복 변환은 아직 검증하지 않았다.
