# BLIP Camera Captioning System

실시간 카메라 피드를 BLIP AI 모델로 분석하여 이미지 캡션을 생성하는 시스템입니다.

## 주요 기능

- **실시간 이미지 캡션 생성**: BLIP/BLIP-2 모델 사용
- **듀얼 스크린 디스플레이**: 카메라 피드 + 캡션 텍스트
- **중국 고전 문서 스타일**: 수직 텍스트 레이아웃
- **2K 해상도 지원**: 2560x1440 고해상도 디스플레이
- **타이핑 애니메이션**: 글자가 하나씩 나타나는 효과
- **GPU 가속 지원**: CUDA/MPS 자동 감지

## 디스플레이 특징

- 검은 배경에 흰 글자
- 공백을 하이픈으로 자동 변환
- 오른쪽에서 왼쪽으로 컬럼 배치 (중국 고전 문서 스타일)
- 새 캡션이 오른쪽에 추가
- 화면이 가득 차면 왼쪽부터 자동 삭제

## 설치 및 실행

### 1. 가상환경 생성 및 활성화
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 실행
```bash
python main_enhanced.py --interactive
python main_enhanced.py --config config.yaml
```


## 설정 조정

[dual_screen_display.py](dual_screen_display.py) 파일의 상단에서 설정값을 조정할 수 있습니다:

```python
WINDOW_WIDTH = 2560        # 화면 너비 (2K: 2560, 4K: 3840)
WINDOW_HEIGHT = 1440       # 화면 높이 (2K: 1440, 4K: 2160)
FONT_SIZE = 24             # 글자 크기
COLUMN_WIDTH = 10          # 컬럼 간격
CHAR_SPACING = 2           # 글자 간격
```

## 프로젝트 구조

```
rain_of_ksana/
├── main.py                  # 메인 실행 파일
├── blip_model.py            # BLIP 모델 관리
├── blip2_model.py           # BLIP-2 모델 관리
├── camera_manager.py        # 카메라 관리
├── caption_engine.py        # 캡션 엔진 (메인 오케스트레이터)
├── dual_screen_display.py   # 듀얼 스크린 디스플레이
├── requirements.txt         # 의존성 패키지
├── requirements-dev.txt     # 개발 도구
├── scripts/                 # 설치 및 설정 스크립트
│   ├── GPU_SETUP_GUIDE.md
│   ├── install_gpu.bat
│   └── install_gpu_pytorch.py
└── assets/
    └── fonts/
        └── Acumin_Variable_Concept.ttf
```

## 사용법

### 명령어 옵션
- `--dual-screen`: 듀얼 스크린 모드 활성화
- `--show-camera`: 단일 카메라 창 표시
- `--interval N`: 캡션 생성 간격 (초)
- `--blip2`: BLIP-2 모델 사용
- `--camera N`: 카메라 인덱스 (기본: 0)
- `--list-cameras`: 사용 가능한 카메라 목록 확인
- `--status`: 시스템 상태 확인
- `--backend`: 카메라 백엔드 선택 (auto, dshow, msmf 등)

### 종료 방법
- 화면에서 `q` 키 누르기
- 터미널에서 `Ctrl+C` 누르기

### 테마 설정
- `--interactive` 모드에서 다크/라이트 테마 선택 가능
- 다크 모드: 검은 배경, 흰 글자
- 라이트 모드: 흰 배경, 검은 글자

### 비 효과 (Rain Effect)
- `--interactive` 모드에서 비 효과 활성화 및 설정 가능
- **rain_effect_1**: 텍스트를 통과하는 이동하는 공백 (moving blanc)
  - 단어가 `word` → `ord` → `w rd` → `wo d` → `wor` → `word` 처럼 변화
  - 비 크기 (rain_size): 연속된 공백의 개수 (1-5)
  - 비 빈도 (rain_frequency): 프레임당 열당 확률 (0.01-1.0, 높을수록 비가 많음)

## 기술 스택

- **Python 3.11+** (3.12 권장)
- **PyTorch**: AI 모델 실행
- **HuggingFace Transformers**: BLIP/BLIP-2 모델
- **OpenCV**: 카메라 및 이미지 처리
- **Pillow**: 이미지 및 폰트 렌더링
- **NumPy**: 수치 연산

## GPU 가속 설정

GPU 가속을 위한 상세한 설정 방법은 [scripts/GPU_SETUP_GUIDE.md](scripts/GPU_SETUP_GUIDE.md)를 참고하세요.

### 빠른 GPU 설정 (Windows)
```bash
# Python 3.11 또는 3.12 가상환경 생성
python3.11 -m venv venv_gpu
.\venv_gpu\Scripts\Activate.ps1

# GPU 지원 PyTorch 설치
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### GPU 테스트
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

## 문제 해결

### 카메라가 열리지 않는 경우
```bash
# 사용 가능한 카메라 목록 확인
python main.py --list-cameras

# 다른 카메라 인덱스 시도
python main.py --dual-screen --camera 1

# 다른 백엔드 시도 (Windows)
python main.py --dual-screen --backend dshow
```

### 폰트가 로드되지 않는 경우
- [assets/fonts/Acumin_Variable_Concept.ttf](assets/fonts/Acumin_Variable_Concept.ttf) 파일이 존재하는지 확인
- 없으면 시스템 기본 폰트로 자동 대체됩니다

### 성능이 느린 경우
```bash
# GPU 가속 사용 (권장)
# scripts/GPU_SETUP_GUIDE.md 참고

# 또는 더 긴 간격으로 실행
python main.py --dual-screen --interval 10

# BLIP-2 대신 BLIP 사용
python main.py --dual-screen --interval 5
```

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.