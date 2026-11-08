# Pixel Art Character Generator

**Project Specification & Codex Handoff**

- Version: 0.2.0
- Status: Planning → Implementation
- Type: Generative AI / Game Development Tools
- Environment: Local-first
- Primary Device: MacBook M2 Pro
- Target: Personal-use pixel art generation tool

---

## 1. 프로젝트 개요

### 1.1. 목적

사용자가 자연어로 원하는 캐릭터를 설명하고 장르, 테마, 크기 등을 설정하면 게임에서 사용 가능한 도트그래픽 캐릭터를 생성하는 AI 모델과 로컬 서비스를 개발한다.

최종 생성 모델은 자체적으로 학습한 **Pixel Transformer**를 사용하며, 기존 상용 이미지 생성 모델에 의존하지 않고 로컬에서 추론할 수 있어야 한다.

### 1.2. 핵심 목표

1. 픽셀 토큰을 직접 생성하는 Transformer 개발
2. 프롬프트 및 생성 조건을 반영하는 캐릭터 생성
3. Teacher–Student 및 GAN 기반 모델 성능 개선 연구
4. 로컬 환경에서 학습 및 추론
5. 게임에서 사용 가능한 PNG 스프라이트 생성
6. 외부 이미지 생성 API에 대한 배포 의존성 제거
7. 개인용 도구로 시작하여 향후 확장 가능한 구조 확보

### 1.3. 개발 원칙

- **Model Independence:** 핵심 이미지 생성 모델 자체 개발
- **Local-first:** 학습과 추론 모두 로컬에서 실행
- **Modular Architecture:** 생성 모델, 학습, 추론, 서비스 분리
- **Reproducibility:** 데이터, 학습 설정, 체크포인트, Seed 관리
- **License-aware:** 데이터 및 모델 이용 조건 확인
- **Research-oriented:** 아키텍처와 학습 방법을 비교·평가할 수 있는 구조

---

## 2. 기능 요구사항

### 2.1. 사용자 입력

| 항목 | 설명 |
|---|---|
| Prompt | 생성할 캐릭터의 자연어 설명 |
| Genre | RPG, Platformer, Action 등 |
| Theme | Fantasy, Sci-Fi, Modern 등 |
| Size | 16×16, 32×32, 64×64 등 |
| Seed | 생성 결과 재현 |
| View | Front, Side, Back (향후) |
| Palette | 색상 팔레트 선택 (향후) |

V1에서는 32×32 단일 해상도로 시작한다.

다중 해상도는 아키텍처가 확장 가능하도록 설계하되, 초기 학습 범위에는 포함하지 않는다.

### 2.2. 출력

- 실제 픽셀 그리드 기반 이미지
- PNG / RGBA
- 투명 배경
- Nearest-neighbor 기반 확대 미리보기
- 원본 픽셀 해상도 유지
- 게임에서 사용할 수 있도록 파일 내보내기

### 2.3. 서비스 기능

- 프롬프트 입력
- 장르 및 테마 선택
- 캐릭터 생성
- Seed 지정 및 재생성
- 생성 결과 미리보기
- PNG 저장
- 생성 이력 관리
- 체크포인트 선택 및 모델 변경

---

## 3. 생성 모델 아키텍처

### 3.1. 최종 모델

**Conditional Masked Pixel Transformer**

이미지를 픽셀 단위의 이산 토큰으로 표현하고, 입력 조건에 따라 픽셀 토큰을 생성하는 Transformer를 직접 구현한다.

기본 구조:

1. Text Encoder
2. Genre / Theme Embedding
3. Condition Projection
4. Pixel Token Embedding
5. 2D Positional Encoding
6. Bidirectional Transformer
7. Pixel Token Prediction Head
8. Iterative Masked Sampling
9. Palette Decoder

### 3.2. 모델 입력 및 출력

입력:

- Text Prompt
- Genre
- Theme
- Image Size
- Random Seed

출력:

- 2D Pixel Token Grid
- RGBA PNG Sprite

기본 생성 목표는 다음과 같다.

`P(Image | Prompt, Genre, Theme, Size)`

### 3.3. V1 모델 초기 설정

| 항목 | 초기 사양 |
|---|---|
| Architecture | Masked Pixel Transformer |
| Image Resolution | 32×32 |
| Pixel Tokens | 1024 |
| Palette | 32 Colors + Transparency |
| Mask Token | 별도 특수 토큰 |
| Transformer Layers | 4–6 |
| Hidden Dimension | 192–256 |
| Attention Heads | 4–8 |
| Positional Encoding | 2D |
| Optimizer | AdamW |
| Primary Loss | Masked Cross-Entropy |

이 값들은 확정된 최적 하이퍼파라미터가 아니라 초기 실험값이다.

### 3.4. Pixel Tokenization

각 픽셀을 색상 토큰으로 표현한다.

32색 팔레트와 투명 토큰 하나를 사용하면 총 33개의 출력 클래스를 가진다.

학습용 `[MASK]` 토큰은 출력 색상 클래스와 별도로 관리한다.

V1에서는 고정 팔레트와 이진 알파를 사용한다.

이미지는 다음과 같이 처리한다.

`RGBA Image → Palette Mapping → Pixel Tokens → Transformer`

생성된 토큰은 반대 과정을 거쳐 PNG로 변환한다.

### 3.5. Text Conditioning

Text Encoder를 통해 프롬프트를 벡터로 변환한다.

장르 및 테마는 별도 임베딩으로 표현하고, Transformer에 조건으로 전달한다.

- 경량 사전학습 Text Encoder 사용 가능
- Text Encoder는 초기 학습에서 동결 가능
- 이미지 Generator 자체는 직접 구현
- 텍스트 인코더의 라이선스 별도 확인
- 한국어 지원 성능은 실제 테스트로 검증

### 3.6. Generation Strategy

Masked Generative Modeling을 사용한다.

1. 전체 픽셀 토큰을 Mask로 초기화
2. Transformer가 각 토큰의 색상 확률 예측
3. 일부 토큰 확정
4. 불확실한 토큰 재예측
5. 반복적으로 이미지 완성

자기회귀 방식과 비교할 수 있도록 샘플링 모듈을 독립적으로 설계한다.

---

## 4. 학습 시스템

최종 학습 대상은 하나의 Pixel Transformer이며, 기본 학습과 두 가지 선택적 고도화 파이프라인으로 구성한다.

### 4.1. Pipeline A — Base Training

**목적:** 자체 Pixel Transformer의 기본 생성 능력 확보

구성:

- Licensed Pixel Art Dataset
- Palette Tokenizer
- Conditional Pixel Transformer
- Masked Token Prediction
- Cross-Entropy Loss

학습 과정:

1. 이미지와 조건 데이터 로드
2. 픽셀 토큰 변환
3. 랜덤 Mask 적용
4. 조건부 Transformer 예측
5. Masked Cross-Entropy 계산
6. 가중치 업데이트
7. 체크포인트 저장

`L_base = L_masked`

**V1 필수 구현 범위.**

### 4.2. Pipeline B — Teacher–Student Distillation

**목적:** 사전학습된 생성 모델의 능력을 자체 Pixel Transformer로 전달

#### Teacher

- 사전학습된 Diffusion 계열 생성 모델
- 초기 구상은 상용 Diffusion 모델 활용
- 학습 중 일반적으로 가중치 동결
- 참조 이미지 또는 증류 학습 신호 제공

#### Student

- 자체 Pixel Transformer
- 실제 학습 및 성능 개선 대상

기본 흐름:

`Input Conditions → Teacher → Permitted Reference Outputs → Student Training`

서로 다른 아키텍처를 직접 대응시키는 증류가 어려울 수 있으므로, 실제 Teacher가 제공하는 출력과 접근 가능한 학습 신호에 따라 증류 방법을 별도로 결정한다.

#### 라이선스 조건

상용 Diffusion 모델을 Teacher로 사용한다고 해서 자동으로 자체 모델 학습에 활용할 수 있는 것은 아니다.

다음 사항을 반드시 확인한다.

- 생성 이미지의 모델 학습 활용 가능 여부
- 모델 증류 허용 여부
- 상업적 사용 권한
- 출력물 및 파생 모델에 대한 제한
- 추가 계약 필요 여부

**V2 이후 선택적 구현.**

### 4.3. Pipeline C — GAN Training

**목적:** Pixel Transformer의 생성 품질 개선

#### Generator

- 자체 Pixel Transformer
- Pipeline A 또는 B로 사전학습된 가중치 사용

#### Discriminator

- 자체 CNN 기반 조건부 판별기
- 실제 픽셀아트와 생성 픽셀아트 비교
- 조건 일치 및 시각적 품질 학습 신호 제공

기본 흐름:

`Generator → Generated Image → Discriminator ↔ Real Images`

Generator 손실:

`L_G = L_masked + λ_adv × L_adv`

픽셀 토큰이 이산적이므로 Gumbel-Softmax 등의 미분 가능한 근사 기법을 실험한다.

GAN 학습은 기본 모델과 비교하여 실제 품질 개선이 확인되는 경우에 적용한다.

**V2 이후 선택적 구현.**

### 4.4. 학습 파이프라인 관계

- Pipeline A: 기본 생성 모델 학습
- Pipeline B: Teacher 지식 증류
- Pipeline C: GAN 미세조정

B와 C는 독립적으로 실험할 수 있어야 한다.

최종 모델의 중심은 Pixel Transformer이며, B와 C를 모두 적용해야 한다는 전제는 두지 않는다.

---

## 5. 데이터셋 설계

### 5.1. 데이터 구조

각 이미지에 다음 정보를 기록한다.

- Image Path
- Prompt / Caption
- Genre
- Theme
- Width / Height
- Palette
- Source
- License
- Character ID

메타데이터 형식은 JSONL을 기본으로 사용한다.

### 5.2. 데이터 정책

허용 가능한 데이터:

- 직접 제작한 픽셀아트
- 학습에 필요한 권리를 확보한 오픈 에셋
- 별도 사용 허락을 받은 데이터
- 학습 활용이 명시적으로 허용된 합성 데이터

데이터의 출처와 이용 조건을 반드시 추적한다.

개인용 사용이더라도 장기적인 프로젝트 활용과 게임 출시 가능성을 고려하여 라이선스를 관리한다.

자체 모델을 학습한다고 모든 저작권 문제가 자동으로 해결되는 것은 아니다.

### 5.3. 데이터 전처리

- RGBA 정규화
- 크기 및 정렬 검증
- 팔레트 양자화
- 픽셀 토큰 변환
- 메타데이터 인코딩
- 중복 이미지 검사
- Train / Validation / Test 분할

캐릭터 ID를 기준으로 데이터 분할을 관리하여 유사 이미지의 데이터 누출을 방지한다.

### 5.4. 데이터 수집 관련 위험

프롬프트 조건부 생성 모델에서는 이미지 수뿐 아니라 이미지 설명과 조건 라벨의 품질이 중요하다.

특히 장르와 테마의 차이를 학습하려면 구별 가능한 라벨과 충분한 예시가 필요하다.

---

## 6. 기술 스택

### 6.1. Core / Machine Learning

| 기술 | 용도 |
|---|---|
| Python 3.11+ | 주요 개발 언어 |
| PyTorch | 모델 및 학습 구현 |
| PyTorch MPS | Apple Silicon GPU |
| Hugging Face Transformers | Text Encoder |
| Pillow | 이미지 처리 |
| NumPy | 픽셀 및 배열 처리 |
| TensorBoard | 실험 시각화 |
| safetensors | 모델 가중치 저장 |

### 6.2. Advanced Training

| 기술 | 용도 |
|---|---|
| Hugging Face Diffusers | Teacher 실행 및 연구 |
| PyTorch CNN | Discriminator |
| Gumbel-Softmax | 이산 토큰 학습 근사 |
| MLflow | 확장된 실험 관리, 선택 사항 |

### 6.3. Backend

| 기술 | 용도 |
|---|---|
| FastAPI | 로컬 생성 API |
| Pydantic | 요청 및 응답 검증 |
| Uvicorn | ASGI Server |
| SQLite | 생성 이력 및 메타데이터 |
| SQLAlchemy | DB 접근, 필요 시 |

### 6.4. Frontend

| 기술 | 용도 |
|---|---|
| Vue 3 | Web UI |
| TypeScript | 타입 안전성 |
| Vite | 개발 및 빌드 |
| Pinia | 복잡한 상태 관리가 필요해질 때 도입 |

### 6.5. Development Tools

| 기술 | 용도 |
|---|---|
| uv | Python 환경 및 패키지 관리 |
| Git | 소스 버전 관리 |
| pytest | 자동 테스트 |
| Ruff | Lint / Format |
| YAML | 학습 및 모델 설정 |
| Git LFS 또는 별도 저장소 | 대용량 파일 관리, 필요 시 |

Docker는 V1의 필수 기술에서 제외한다.

학습과 추론은 macOS 호스트의 PyTorch MPS 환경을 우선 사용한다.

---

## 7. 서비스 아키텍처

### 7.1. 전체 구조

`Vue Web UI → FastAPI → Model Runtime → Pixel Decoder → PNG`

서비스는 다음 구성 요소로 분리한다.

**Frontend**

- 입력 폼
- 생성 요청
- 결과 미리보기
- PNG Export
- 생성 기록

**Backend**

- 입력 검증
- 모델 및 체크포인트 관리
- 생성 작업 실행
- 파일 및 메타데이터 저장
- API 응답

**Model Runtime**

- Text / Condition Encoder
- Pixel Transformer
- Masked Sampling
- Palette Decoder

### 7.2. API

초기 API:

- `POST /api/v1/generate`
- `GET /api/v1/generations/{id}`
- `GET /api/v1/models`
- `GET /api/v1/health`

향후 API:

- 모델 체크포인트 변경
- 학습 작업 제어
- 학습 상태 조회
- 실험 결과 조회

V1에서는 생성 API를 우선 구현한다.

### 7.3. 배포 모델

로컬 개발 및 개인 사용을 기본으로 한다.

- 외부 이미지 생성 API 불필요
- 로컬 체크포인트 사용
- 로컬 파일시스템 저장
- FastAPI와 Vue 실행
- 인터넷 연결 없이 추론 가능

Text Encoder 역시 로컬에 필요한 파일을 보유해야 한다.

---

## 8. 프로젝트 디렉터리

권장 초기 구조:

    pixel-art-generator/
    ├── apps/
    │   └── web/
    ├── services/
    │   └── api/
    ├── src/
    │   └── pixelgen/
    │       ├── models/
    │       │   ├── transformer/
    │       │   ├── encoders/
    │       │   └── discriminator/
    │       ├── data/
    │       ├── training/
    │       │   ├── base/
    │       │   ├── distillation/
    │       │   └── adversarial/
    │       ├── inference/
    │       └── evaluation/
    ├── configs/
    ├── datasets/
    ├── checkpoints/
    ├── outputs/
    ├── experiments/
    ├── scripts/
    ├── tests/
    ├── docs/
    │   ├── spec.md
    │   ├── architecture.md
    │   ├── tech-stack.md
    │   ├── roadmap.md
    │   └── decisions/
    ├── pyproject.toml
    ├── README.md
    └── AGENTS.md

`datasets/`, `checkpoints/`, `outputs/` 등에는 필요한 빈 디렉터리만 추적하고 대용량 데이터와 가중치는 기본적으로 Git에서 제외한다.

---

## 9. 평가 및 실험

### 9.1. 평가 기준

- 이미지 품질
- 프롬프트 조건 일치도
- 장르 및 테마 표현
- 캐릭터 형태의 명확성
- 생성 이미지 다양성
- 실제 학습 이미지와의 근접 중복 여부
- 추론 속도
- 학습 시간
- 메모리 사용량
- 로컬 실행 안정성

### 9.2. 실험 비교

| Experiment | 구성 |
|---|---|
| A | Base Transformer |
| B | Base + Teacher Distillation |
| C | Base + GAN |
| D | Base + Teacher + GAN |

고정된 평가 데이터와 프롬프트를 사용하여 비교한다.

V1에서는 Experiment A를 구현하고 평가한다.

---

## 10. 개발 로드맵

### Phase 0 — Project Foundation

- 저장소 초기화
- Python 개발 환경 구성
- 기본 디렉터리 구조
- 설정 관리
- 테스트 환경
- 프로젝트 문서 및 AGENTS.md

### Phase 1 — Pixel Representation

- Palette 정의
- Pixel Tokenizer 구현
- RGBA → Token 변환
- Token → RGBA 변환
- 이미지 데이터 로더
- 전처리 및 검증 테스트

**완료 조건:** 이미지의 토큰화와 복원이 일관되게 동작한다.

### Phase 2 — Base Model

- Condition Encoder
- Transformer 구현
- Masked Token Prediction
- Sampling 알고리즘
- 모델 저장 및 복원

**완료 조건:** 작은 합성 데이터셋에서 학습하고 이미지를 생성할 수 있다.

### Phase 3 — Training Pipeline

- 실제 픽셀아트 데이터셋 연결
- 학습 루프
- Validation
- Checkpointing
- TensorBoard
- 샘플 이미지 기록
- 모델 성능 평가

**완료 조건:** 32×32 조건부 캐릭터 생성 실험을 재현할 수 있다.

### Phase 4 — Local Service

- FastAPI
- 모델 추론 엔진
- Vue Web UI
- PNG Export
- 생성 이력 관리

**완료 조건:** 로컬 웹에서 프롬프트를 입력하고 스프라이트를 생성할 수 있다.

### Phase 5 — Teacher–Student Research

- Teacher 모델 후보 조사
- 라이선스 검증
- 증류 데이터 및 손실 함수 설계
- Student Fine-Tuning
- 성능 비교

### Phase 6 — GAN Research

- CNN Discriminator 구현
- 적대적 손실 함수
- 이산 토큰의 그래디언트 처리
- Generator Fine-Tuning
- 성능 비교

### Phase 7 — Advanced Generation

- 다중 해상도
- 팔레트 지정
- 시점 제어
- 캐릭터 일관성
- 애니메이션
- Sprite Sheet

---

## 11. 기술적 위험 및 제약

### 11.1. 모델 품질

소형 Transformer가 고품질 캐릭터를 생성한다는 보장은 없다.

특히 학습 데이터 규모, 텍스트 조건 정보량, 캐릭터 형태 표현이 주요 제약 요소다.

### 11.2. 하드웨어

M2 Pro를 대상으로 소형 모델부터 실험한다.

MPS 지원 연산, 통합 메모리 용량, 배치 크기에 따라 실제 학습 가능 범위가 달라질 수 있다.

### 11.3. GAN 안정성

Discrete Pixel Token과 적대적 학습의 결합은 학습 불안정성이 발생할 수 있다.

GAN 도입을 필수 조건으로 두지 않는다.

### 11.4. Teacher 모델

모델 사용 권한뿐 아니라 Teacher 출력으로 자체 모델을 학습할 수 있는지도 확인해야 한다.

### 11.5. 결과물 저작권

자체 모델이라도 데이터 권리, 기존 캐릭터와의 실질적 유사성, AI 생성물의 권리 귀속 문제가 별도로 남는다.

---

## 12. V1 완료 기준

- [ ] Pixel Transformer가 구현되어 있다.
- [ ] 이미지 토큰화 및 복원이 가능하다.
- [ ] 모델 학습과 체크포인트 저장이 가능하다.
- [ ] 프롬프트·장르·테마를 조건으로 전달할 수 있다.
- [ ] 32×32 픽셀아트를 생성한다.
- [ ] 유효한 RGBA PNG로 변환된다.
- [ ] FastAPI를 통한 생성 요청이 가능하다.
- [ ] Vue UI에서 결과를 확인하고 저장할 수 있다.
- [ ] 인터넷 연결 없이 추론할 수 있다.
- [ ] 테스트 및 실험 기록을 남길 수 있다.

V1 완료는 모든 프롬프트에서 고품질 결과가 나온다는 의미는 아니다. 생성 품질은 별도 평가를 통해 확인한다.

---

## 13. Codex 작업 지침

이 프로젝트의 구현을 담당하는 AI 코딩 에이전트는 다음 사항을 따른다.

### 기본 원칙

1. 본 문서를 구현의 기준 명세로 사용한다.
2. 프로젝트를 모듈화하여 각 구성 요소가 독립적으로 테스트될 수 있도록 구현한다.
3. Pixel Transformer는 PyTorch 기반으로 직접 구현한다.
4. 기존 완성형 이미지 생성 모델을 핵심 Generator로 대체하지 않는다.
5. V1에서는 Base Training만 구현하고, Teacher–Student와 GAN은 확장 가능성만 확보한다.
6. 학습 코드와 서비스 코드를 명확히 분리한다.
7. 학습 설정과 체크포인트가 재현 가능하도록 설계한다.
8. macOS MPS를 기본 대상으로 하되 CPU 실행도 고려한다.
9. 대용량 가중치 및 데이터셋을 Git에 직접 포함하지 않는다.
10. 미확정 연구 설계는 임의로 확정하지 않고, 근거와 대안을 문서화한다.

### 구현 우선순위

**Pixel Tokenizer → Dataset → Transformer → Training → Sampling → Evaluation → API → Web UI**

우선 최소 모델이 학습 및 추론되는 과정을 완성하고, 이후 성능 고도화와 서비스 확장을 진행한다.

### 첫 작업

1. 현재 프로젝트 디렉터리 및 Git 상태 확인
2. `docs/spec.md` 작성
3. `docs/tech-stack.md` 작성
4. `docs/architecture.md` 작성
5. `docs/roadmap.md` 작성
6. `AGENTS.md` 작성
7. `pyproject.toml` 및 개발 도구 구성
8. V0 모델 실험에 필요한 최소 디렉터리 및 테스트 환경 구축

첫 작업에서는 본격적인 모델 학습이나 대규모 의존성 설치보다, 구현 기반을 만들고 프로젝트 구조를 검증하는 데 집중한다.

---

## 14. 최종 프로젝트 방향

**핵심 연구 대상:** Conditional Pixel Transformer

**기본 학습:** Masked Token Prediction

**확장 학습 1:** Diffusion Teacher 기반 Knowledge Distillation

**확장 학습 2:** Conditional GAN 기반 Adversarial Fine-Tuning

**최종 서비스 모델:** 자체 Pixel Transformer + 필수 Condition Encoder + Pixel Decoder

**최종 결과물:** 로컬에서 실행 가능한 프롬프트 기반 픽셀아트 캐릭터 생성 도구

장기적으로 게임 개발자가 원하는 캐릭터를 자연어로 생성하고, 해당 결과를 실제 게임 에셋으로 활용할 수 있는 독립적인 생성형 AI 시스템을 목표로 한다.
