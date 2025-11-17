# BLIP Camera Captioning - Docker Image
# Supports GPU acceleration with CUDA

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    v4l-utils \
    libv4l-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install PyTorch with CUDA support (adjust CUDA version as needed)
# For CUDA 11.8: --index-url https://download.pytorch.org/whl/cu118
# For CUDA 12.1: --index-url https://download.pytorch.org/whl/cu121
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cu121 \
    torch torchvision torchaudio

# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create assets directory if it doesn't exist
RUN mkdir -p assets/fonts

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV TOKENIZERS_PARALLELISM=false

# Expose port for Ollama (if used)
EXPOSE 11434

# Default command
CMD ["python", "main.py", "--interactive"]

