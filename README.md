# 🤖 BLIP Camera Captioning System

실시간 카메라 피드를 BLIP AI 모델로 분석하여 이미지 캡션을 생성하고, 중국 고전 문서 스타일로 표시하는 시스템입니다.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange.svg)](https://pytorch.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## ✨ 주요 기능

- 🎥 **실시간 이미지 캡션 생성**: BLIP/BLIP-2 모델 사용
- 🖥️ **멀티 스크린 디스플레이**: 1-3개의 독립적인 텍스트 스크린 지원
- 📜 **중국 고전 문서 스타일**: 수직 텍스트 레이아웃 (오른쪽→왼쪽)
- 🎨 **타이핑 애니메이션**: 글자가 하나씩 나타나는 효과
- 🦙 **Ollama 통합**: LLM 기반 텍스트 요약 기능
- ⚡ **GPU 가속 지원**: CUDA/MPS 자동 감지
- 🐳 **Docker 지원**: 컨테이너 기반 실행 가능

## 🎨 디스플레이 특징

- **검은 배경**에 **흰 글자** (다크 모드)
- **공백 → 하이픈** 자동 변환
- **오른쪽에서 왼쪽** 컬럼 배치 (중국 고전 문서 스타일)
- **새 캡션**이 **오른쪽**에 추가
- **화면 가득 차면** **왼쪽부터 자동 삭제**
- **멀티 스크린**: 화면이 가득 차면 다음 스크린으로 오버플로우

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone <repository-url>
cd rain_of_ksana
```

### 2. 가상환경 생성 및 활성화

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

**GPU 지원 (CUDA 12.1):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### 4. 실행

**인터랙티브 설정 (권장):**
```bash
python main.py --interactive
```

**빠른 시작:**
```bash
# 기본 실행 (단일 스크린)
python main.py

# 멀티 스크린 (3개) + BLIP-2
python main.py --screens 3 --blip2

# 설정 파일 사용
python main.py --config config.yaml
```

## 📖 사용법

### 기본 명령어

#### 설정 옵션
- `--interactive`, `-i`: 인터랙티브 설정 마법사 실행
- `--config`, `-c FILE`: 설정 파일 로드 (YAML/JSON)
- `--screens N`: 텍스트 스크린 개수 설정 (1-3)
- `--blip2`: BLIP-2 모델 사용 (더 정확하지만 느림)
- `--dual-interval`: 듀얼 인터벌 모드 활성화 (Ollama 요약 포함)
- `--interval N`: 캡션 생성 간격 (초)

#### 카메라 옵션
- `--camera N`: 카메라 인덱스 지정 (기본: 0)
- `--list-cameras`: 사용 가능한 카메라 목록 표시
- `--auto-camera`: 첫 번째 사용 가능한 카메라 자동 선택
- `--backend NAME`: 카메라 백엔드 지정 (auto, dshow, msmf 등)
- `--show-camera`: 카메라 피드 창 표시

#### 시스템 옵션
- `--status`: 시스템 상태 확인
- `--test-ollama`: Ollama 연결 테스트

### 사용 예제

```bash
# 카메라 목록 확인
python main.py --list-cameras

# 시스템 상태 확인
python main.py --status

# 3개 스크린 + BLIP-2 + 카메라 표시
python main.py --screens 3 --blip2 --show-camera

# 듀얼 인터벌 모드 (Ollama 요약 포함)
python main.py --dual-interval --screens 2

# 특정 카메라 사용
python main.py --camera 1 --interval 5
```

### 종료 방법

- 화면에서 `q` 키 누르기
- 터미널에서 `Ctrl+C` 누르기

## ⚙️ 설정

### 설정 파일 (config.yaml)

설정은 `config.yaml` 파일을 통해 관리됩니다. `config.example.yaml`을 참고하여 복사하세요:

```bash
cp config.example.yaml config.yaml
```

주요 설정 항목:

```yaml
# 디스플레이 설정
display:
  text_screen_count: 3        # 스크린 개수 (1-3)
  window_width: 2560           # 창 너비
  window_height: 1440          # 창 높이
  font_size: 48               # 폰트 크기
  typing_speed: 0.03          # 타이핑 애니메이션 속도

# 모델 설정
model:
  type: "blip2"               # "blip" 또는 "blip2"
  use_gpu: "auto"             # "auto", true, false

# 카메라 설정
camera:
  index: 0                    # 카메라 인덱스
  backend: "auto"             # 백엔드
  show_camera: true           # 카메라 창 표시

# 타이밍 설정
timing:
  dual_interval_mode: true    # 듀얼 인터벌 모드
  interval_short: 5          # 짧은 인터벌 (초)
  interval_long: 15          # 긴 인터벌 (초)

# Ollama 설정
ollama:
  enabled: true               # Ollama 활성화
  model: "llama3.2:3b"       # 사용할 모델
  base_url: "http://localhost:11434"
```

## 📁 프로젝트 구조

```
rain_of_ksana/
├── main.py                  # 메인 진입점
├── requirements.txt         # 핵심 의존성
├── config.yaml              # 설정 파일
├── config.example.yaml      # 설정 예제
├── Dockerfile               # Docker 이미지 빌드
├── docker-compose.yml       # Docker Compose 설정
├── README.md                # 이 파일
│
├── src/                     # 소스 코드
│   ├── __init__.py
│   ├── blip_model.py        # BLIP 모델 관리
│   ├── blip2_model.py      # BLIP-2 모델 관리
│   ├── camera_manager.py    # 카메라 관리
│   ├── caption_buffer.py    # 캡션 버퍼 관리
│   ├── caption_engine_enhanced.py  # 향상된 캡션 엔진
│   ├── caption_engine.py   # 기본 캡션 엔진
│   ├── cascading_screen_display.py  # 캐스케이딩 스크린 디스플레이
│   ├── config_manager.py    # 설정 관리
│   ├── dual_screen_display.py  # 듀얼 스크린 디스플레이
│   ├── multi_screen_display.py  # 멀티 스크린 디스플레이
│   └── ollama_integration.py  # Ollama 통합
│
├── tests/                   # 테스트
│   └── test_system.py       # 시스템 테스트
│
├── docs/                    # 문서
│   ├── README_ENHANCED.md   # 상세 가이드
│   ├── QUICKSTART.md        # 빠른 시작 가이드
│   ├── DOCKER.md            # Docker 가이드
│   └── ...
│
├── requirements/            # 추가 requirements
│   ├── requirements-dev.txt
│   └── requirements-macos.txt
│
├── scripts/                 # 스크립트
│   ├── GPU_SETUP_GUIDE.md
│   └── install_gpu.bat
│
└── assets/                  # 리소스
    └── fonts/
        └── Acumin_Variable_Concept.ttf
```

## 🐳 Docker 사용

### 빠른 시작

```bash
# 이미지 빌드
docker-compose build

# 실행
docker-compose up

# 백그라운드 실행
docker-compose up -d
```

### GPU 지원

NVIDIA GPU가 있는 경우 `nvidia-docker2`가 필요합니다:

```bash
# GPU 확인
nvidia-smi

# GPU 지원으로 실행
docker-compose up
```

자세한 내용은 [docs/DOCKER.md](docs/DOCKER.md)를 참고하세요.

## 🔧 기술 스택

- **Python 3.11+** (3.12 권장)
- **PyTorch**: AI 모델 실행
- **HuggingFace Transformers**: BLIP/BLIP-2 모델
- **OpenCV**: 카메라 및 이미지 처리
- **Pillow (PIL)**: 이미지 및 폰트 렌더링
- **NumPy**: 수치 연산
- **PyYAML**: 설정 파일 관리
- **Ollama**: LLM 통합 (선택사항)

## 📋 요구사항

### 필수
- Python 3.11 이상
- 카메라 권한
- 인터넷 연결 (초기 모델 다운로드)

### 권장
- NVIDIA GPU (CUDA 지원) 또는 Apple Silicon (MPS 지원)
- 최소 8GB RAM
- Ollama (듀얼 인터벌 모드 사용 시)

## 🎯 주요 특징

### AI 모델
- **BLIP**: 빠르고 가벼운 기본 모델
- **BLIP-2**: 더 정확하지만 큰 모델 (GPU 권장)

### 디스플레이 모드
- **단일 스크린**: 기본 모드
- **듀얼 스크린**: 카메라 + 텍스트
- **멀티 스크린**: 최대 3개의 독립적인 텍스트 스크린

### 타이밍 모드
- **단일 인터벌**: 일정한 간격으로 캡션 생성
- **듀얼 인터벌**: 짧은 간격으로 캡션 생성, 긴 간격으로 Ollama 요약

### 성능 최적화
- GPU 자동 감지 (CUDA/MPS)
- 메모리 효율적인 캡션 관리
- 비동기 처리 지원

## 🐛 문제 해결

### 카메라가 열리지 않는 경우

```bash
# 사용 가능한 카메라 확인
python main.py --list-cameras

# 다른 카메라 인덱스 시도
python main.py --camera 1
python main.py --camera 2

# 다른 백엔드 시도 (Windows)
python main.py --backend dshow
python main.py --backend msmf
```

### GPU가 인식되지 않는 경우

```bash
# GPU 확인
python -c "import torch; print(torch.cuda.is_available())"

# GPU 지원 PyTorch 재설치
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

자세한 GPU 설정은 [scripts/GPU_SETUP_GUIDE.md](scripts/GPU_SETUP_GUIDE.md)를 참고하세요.

### Ollama 연결 실패

```bash
# Ollama 연결 테스트
python main.py --test-ollama

# Ollama 설치 및 모델 다운로드
# 1. https://ollama.ai/download 방문
# 2. Ollama 설치
# 3. 모델 다운로드
ollama pull llama3.2:3b
```

### 폰트가 로드되지 않는 경우

- `assets/fonts/Acumin_Variable_Concept.ttf` 파일 경로 확인
- 기본 시스템 폰트로 자동 대체됨

### 성능이 느린 경우

```bash
# BLIP-2 대신 BLIP 사용
python main.py --interval 5

# 인터벌 증가
python main.py --interval 10

# GPU 사용 확인
python main.py --status
```

## 📚 추가 문서

- [상세 가이드](docs/README_ENHANCED.md) - 고급 기능 및 설정
- [빠른 시작](docs/QUICKSTART.md) - 단계별 튜토리얼
- [Docker 가이드](docs/DOCKER.md) - Docker 사용법
- [GPU 설정 가이드](scripts/GPU_SETUP_GUIDE.md) - GPU 최적화

## 🧪 테스트

```bash
# 시스템 테스트 실행
python tests/test_system.py
```

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

## 🤝 기여

버그 리포트나 기능 요청은 이슈로 등록해주세요.

## 🙏 감사의 말

- [Salesforce BLIP](https://github.com/salesforce/BLIP) - 이미지 캡션 모델
- [HuggingFace Transformers](https://huggingface.co/transformers) - 모델 라이브러리
- [Ollama](https://ollama.ai/) - LLM 통합

---

**🎉 즐거운 AI 캡션 생성 되세요!**
