# 🐳 Docker Setup Guide

이 가이드는 Docker를 사용하여 BLIP Camera Captioning 시스템을 실행하는 방법을 설명합니다.

## 📋 사전 요구사항

- Docker 및 Docker Compose 설치
- NVIDIA GPU가 있는 경우: [nvidia-docker2](https://github.com/NVIDIA/nvidia-docker) 설치
- Linux: 카메라 접근 권한

## 🚀 빠른 시작

### 1. 이미지 빌드

```bash
docker-compose build
```

### 2. 실행

```bash
# 기본 실행 (interactive mode)
docker-compose up

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 3. 중지

```bash
docker-compose down
```

## ⚙️ 설정

### GPU 사용 (NVIDIA)

`docker-compose.yml`에서 GPU 설정이 이미 포함되어 있습니다. nvidia-docker2가 설치되어 있어야 합니다.

```bash
# GPU 확인
nvidia-smi

# GPU 지원으로 실행
docker-compose up
```

### 카메라 접근

#### Linux
`docker-compose.yml`에 `/dev/video0` 디바이스 마운트가 포함되어 있습니다. 다른 카메라를 사용하려면 수정하세요:

```yaml
devices:
  - /dev/video1:/dev/video1  # 다른 카메라 인덱스
```

#### Windows/macOS
Windows와 macOS에서는 Docker에서 카메라 접근이 제한적입니다. 호스트 시스템에서 직접 실행하는 것을 권장합니다.

### X11 디스플레이 (Linux)

GUI를 표시하려면 X11 소켓을 마운트해야 합니다:

```bash
# X11 권한 허용
xhost +local:docker

# 실행
docker-compose up
```

### 설정 파일 사용

```bash
# config.yaml을 컨테이너에 마운트
docker-compose up -e CONFIG_FILE=/app/config.yaml
```

또는 `docker-compose.yml`에서 volumes 섹션을 수정:

```yaml
volumes:
  - ./config.yaml:/app/config.yaml:ro
```

## 🦙 Ollama 통합

### 옵션 1: 호스트에서 Ollama 실행 (권장)

호스트 시스템에서 Ollama를 실행하고 `network_mode: host`를 사용하여 접근합니다.

```bash
# 호스트에서 Ollama 실행
ollama serve

# Docker 컨테이너에서 접근 (network_mode: host 사용)
docker-compose up
```

### 옵션 2: Docker Compose에서 Ollama 실행

```bash
# Ollama 프로파일과 함께 실행
docker-compose --profile ollama up

# Ollama 모델 다운로드
docker-compose exec ollama ollama pull llama3.2:3b
```

## 📝 사용 예제

### Interactive 모드

```bash
docker-compose run --rm blip-captioning python main.py --interactive
```

### 설정 파일 사용

```bash
docker-compose run --rm blip-captioning python main.py --config config.yaml
```

### 카메라 목록 확인

```bash
docker-compose run --rm blip-captioning python main.py --list-cameras
```

### 시스템 상태 확인

```bash
docker-compose run --rm blip-captioning python main.py --status
```

## 🔧 문제 해결

### GPU가 인식되지 않는 경우

```bash
# nvidia-docker2 확인
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Docker Compose에서 GPU 확인
docker-compose run --rm blip-captioning python -c "import torch; print(torch.cuda.is_available())"
```

### 카메라가 인식되지 않는 경우

```bash
# 호스트에서 카메라 확인
ls -la /dev/video*

# 컨테이너 내부에서 확인
docker-compose run --rm blip-captioning python main.py --list-cameras
```

### 디스플레이 오류

```bash
# X11 권한 확인
xhost

# 권한 허용
xhost +local:docker
```

## 📦 이미지 최적화

더 작은 이미지를 원하는 경우:

1. 멀티 스테이지 빌드 사용
2. 불필요한 패키지 제거
3. `.dockerignore` 최적화

## 🔐 보안 고려사항

- 프로덕션 환경에서는 `xhost +local:docker` 대신 더 안전한 방법 사용
- 설정 파일에 민감한 정보가 포함된 경우 볼륨 마운트 주의
- 네트워크 모드를 적절히 설정

## 📚 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [Docker Compose 문서](https://docs.docker.com/compose/)

