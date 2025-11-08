# 기능 개발 계획서

## 📋 개요
BLIP Camera Captioning 시스템에 고급 기능 추가

**작성일**: 2025-11-08
**상태**: 계획 단계

---

## 🎯 요구사항 분석

### 1. 다중 텍스트 스크린 (최대 3개)
**현재 상태**: 단일 텍스트 스크린
**목표**: 최대 3개의 독립적인 텍스트 스크린 지원

**기술적 고려사항**:
- 각 스크린은 독립적인 창으로 생성
- 화면 배치 자동 조정 (1개, 2개, 3개 레이아웃)
- 각 스크린별 독립적인 캡션 큐 관리

### 2. 단계적 텍스트 생성 및 종합 시스템
**구성 요소**:
- **간격1 (Short Interval)**: 짧은 캡션 생성 주기 (예: 3초)
- **간격2 (Long Interval)**: 긴 캡션 종합 및 출력 주기 (예: 30초)
- **텍스트 종합 엔진**: Ollama 모델 사용

**워크플로우**:
```
[카메라] -> BLIP 캡션 생성 (간격1마다)
         -> 캡션 누적 버퍼에 저장
         -> 간격2가 되면 Ollama로 종합
         -> 종합된 텍스트를 스크린에 출력
```

**예시**:
```
간격1 (3초마다):
- "a person sitting at desk"
- "a laptop computer on table"
- "a coffee cup near keyboard"

간격2 (30초 후) - Ollama 종합:
- "작업 공간에서 노트북으로 작업하는 사람, 책상 위에 커피 한 잔이 놓여있다"
```

### 3. Ollama 통합
**선택 모델**:
- 경량: `llama3.2:3b` (한국어 지원, 빠름)
- 중형: `llama3.1:8b` (더 나은 품질)
- 대형: `qwen2.5:7b` (한국어 특화)

**API 사용**:
```python
import requests

def summarize_captions(captions: list[str]) -> str:
    prompt = f"다음 장면 설명들을 하나의 자연스러운 문장으로 종합해주세요:\n"
    prompt += "\n".join(f"- {cap}" for cap in captions)

    response = requests.post('http://localhost:11434/api/generate',
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        })
    return response.json()['response']
```

### 4. 포괄적 설정 시스템
**설정 항목**:
- `text_screen_count`: 텍스트 스크린 개수 (1-3)
- `model_type`: "blip" 또는 "blip2"
- `typing_speed`: 타이핑 애니메이션 속도 (0.01-0.1초)
- `font_size`: 글자 크기 (12-48)
- `font_path`: 폰트 파일 경로
- `dual_interval_mode`: 이중 시간간격 모드 온/오프
- `interval_short`: 짧은 간격 (초)
- `interval_long`: 긴 간격 (초)
- `ollama_model`: Ollama 모델 이름
- `use_gpu`: GPU 사용 여부 (자동 감지)

**설정 인터페이스 옵션**:
1. **대화형 CLI** (우선 구현): 시작 시 터미널에서 질문
2. **설정 파일** (JSON/YAML): `config.yaml` 파일로 저장
3. **GUI 설정 창** (향후): Tkinter 기반 설정 창

---

## 🏗️ 시스템 아키텍처

### 현재 구조
```
CaptionEngine
├── BLIPModelManager / BLIP2ModelManager
├── CameraManager
└── DualScreenDisplay (단일 스크린)
```

### 새로운 구조
```
CaptionEngine (확장)
├── BLIPModelManager / BLIP2ModelManager
├── CameraManager
├── MultiScreenDisplay (다중 스크린 관리자)
│   ├── TextScreen1
│   ├── TextScreen2
│   └── TextScreen3
├── CaptionBuffer (캡션 누적 버퍼)
├── OllamaIntegration (텍스트 종합 엔진)
└── ConfigManager (설정 관리자)
```

### 새로운 모듈 설계

#### 1. `config_manager.py`
```python
class ConfigManager:
    """설정 관리 시스템"""
    def __init__(self):
        self.config = self.load_or_create_config()

    def load_or_create_config(self) -> dict
    def save_config(self) -> None
    def interactive_setup(self) -> dict  # CLI 대화형 설정
    def validate_config(self) -> bool
```

#### 2. `multi_screen_display.py`
```python
class MultiScreenDisplay:
    """다중 텍스트 스크린 관리자"""
    def __init__(self, screen_count: int = 1):
        self.screens = [TextScreen(i) for i in range(screen_count)]

    def add_caption(self, caption: str, screen_index: int = 0)
    def update_all_screens(self)
    def cleanup(self)
```

#### 3. `ollama_integration.py`
```python
class OllamaIntegration:
    """Ollama 텍스트 종합 엔진"""
    def __init__(self, model: str = "llama3.2:3b"):
        self.model = model
        self.base_url = "http://localhost:11434"

    def check_ollama_available(self) -> bool
    def summarize_captions(self, captions: list[str]) -> str
    def test_connection(self) -> bool
```

#### 4. `caption_buffer.py`
```python
class CaptionBuffer:
    """캡션 누적 및 관리"""
    def __init__(self, max_size: int = 20):
        self.buffer = []
        self.last_summary_time = time.time()

    def add_caption(self, caption: str)
    def get_all_captions(self) -> list[str]
    def clear(self)
    def should_summarize(self, interval_long: float) -> bool
```

---

## 📊 데이터 흐름

### 일반 모드 (단일 간격)
```
Camera -> BLIP -> 캡션 -> MultiScreenDisplay -> 화면 출력
```

### 이중 간격 모드
```
Camera -> BLIP (간격1) -> CaptionBuffer
                            ↓
                    누적 (간격2까지)
                            ↓
                    Ollama 텍스트 종합
                            ↓
                    MultiScreenDisplay -> 화면 출력
```

---

## 🎨 사용자 시나리오

### 시나리오 1: 단일 스크린 + 단일 간격 (기본)
```bash
python main.py --interactive

> 텍스트 스크린 개수 (1-3): 1
> BLIP 모델 (blip/blip2): blip
> 캡션 생성 간격 (초): 5
> 이중 시간간격 모드 사용 (y/n): n
```

### 시나리오 2: 3개 스크린 + 이중 간격 + Ollama
```bash
python main.py --interactive

> 텍스트 스크린 개수 (1-3): 3
> BLIP 모델 (blip/blip2): blip2
> 이중 시간간격 모드 사용 (y/n): y
> 짧은 간격 - 캡션 생성 (초): 3
> 긴 간격 - 텍스트 종합 (초): 30
> Ollama 모델 (llama3.2:3b/llama3.1:8b/qwen2.5:7b): llama3.2:3b
> 폰트 크기 (12-48): 24
> 타이핑 속도 (0.01-0.1): 0.03
```

### 시나리오 3: 설정 파일 사용
```bash
python main.py --config custom_config.yaml
```

---

## ⚙️ 설정 파일 예시 (config.yaml)

```yaml
# 화면 설정
display:
  text_screen_count: 3
  window_width: 2560
  window_height: 1440
  font_size: 24
  font_path: "assets/fonts/Acumin_Variable_Concept.ttf"
  typing_speed: 0.03
  column_width: 10
  char_spacing: 2

# 모델 설정
model:
  type: "blip"  # blip 또는 blip2
  use_gpu: true  # auto, true, false

# 카메라 설정
camera:
  index: 0
  backend: "auto"
  show_camera: true

# 시간 간격 설정
timing:
  dual_interval_mode: true
  interval_short: 3  # 짧은 간격 (초)
  interval_long: 30  # 긴 간격 (초)

# Ollama 설정
ollama:
  enabled: true
  model: "llama3.2:3b"
  base_url: "http://localhost:11434"
  timeout: 30
  prompt_template: |
    다음 장면 설명들을 하나의 자연스러운 한국어 문장으로 종합해주세요.
    시간 순서를 고려하여 이야기처럼 서술하세요:

    {captions}
```

---

## 🔧 구현 단계

### Phase 1: 설정 시스템 구축 ✅
- [ ] `config_manager.py` 작성
- [ ] 대화형 CLI 설정 인터페이스
- [ ] YAML 설정 파일 로드/저장
- [ ] 설정 검증 로직

### Phase 2: Ollama 통합 🔄
- [ ] `ollama_integration.py` 작성
- [ ] Ollama 연결 확인 및 에러 처리
- [ ] 캡션 종합 프롬프트 엔지니어링
- [ ] `caption_buffer.py` 작성

### Phase 3: 다중 스크린 시스템 ⏳
- [ ] `multi_screen_display.py` 작성
- [ ] 화면 레이아웃 자동 조정 (1/2/3개)
- [ ] 독립적인 캡션 큐 관리
- [ ] 기존 `dual_screen_display.py` 리팩토링

### Phase 4: 메인 엔진 통합 ⏳
- [ ] `caption_engine.py` 확장
- [ ] 이중 시간간격 모드 구현
- [ ] 스크린별 캡션 분배 로직
- [ ] GPU 자동 감지 개선

### Phase 5: 테스트 및 문서화 ⏳
- [ ] 단위 테스트 작성
- [ ] 통합 테스트
- [ ] 사용자 매뉴얼 작성
- [ ] README 업데이트

---

## 🚨 위험 요소 및 대응

### 1. Ollama 의존성
**위험**: Ollama가 설치되지 않거나 실행 중이지 않을 수 있음
**대응**:
- Ollama 사용 가능 여부 자동 확인
- 비활성화 시 일반 모드로 폴백
- 설치 가이드 제공

### 2. 다중 창 성능
**위험**: 3개 창 동시 렌더링으로 성능 저하
**대응**:
- 효율적인 렌더링 최적화
- GPU 가속 적극 활용
- 프레임레이트 제한

### 3. 설정 복잡도
**위험**: 설정 항목이 너무 많아 사용자 혼란
**대응**:
- 합리적인 기본값 제공
- Preset 설정 (Simple/Advanced/Expert)
- 단계별 가이드

### 4. 메모리 사용량
**위험**: 캡션 버퍼 누적으로 메모리 증가
**대응**:
- 버퍼 최대 크기 제한
- 주기적 정리
- 메모리 사용량 모니터링

---

## 📚 참고 자료

- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [OpenCV Multi-Window](https://docs.opencv.org/4.x/d7/dfc/group__highgui.html)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)

---

## ✅ 완료 기준

- [ ] 모든 설정 항목이 정상 작동
- [ ] 1/2/3 스크린 모드가 모두 작동
- [ ] Ollama 텍스트 종합이 자연스러움
- [ ] 이중 시간간격 모드가 정확히 작동
- [ ] GPU 가속이 제대로 동작
- [ ] 에러 처리가 견고함
- [ ] 문서화 완료

---

**다음 단계**: Ollama 연결 테스트 및 `config_manager.py` 구현
