# GPU Setup Guide for BLIP Camera Captioning

## Current Issue
You have Python 3.14, which is very new. PyTorch 2.9.0 for Python 3.14 only has CPU builds available, not CUDA builds.

## Solutions

### Option 1: Use Python 3.11 or 3.12 (Recommended)
1. Install Python 3.11 or 3.12 from python.org
2. Create a new virtual environment:
```bash
python3.11 -m venv venv_gpu
# or
python3.12 -m venv venv_gpu
```
3. Activate the new environment:
```bash
venv_gpu\Scripts\Activate.ps1
```
4. Install CUDA-enabled PyTorch:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
5. Install other dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: Use Conda (Alternative)
1. Install Miniconda or Anaconda
2. Create a new environment:
```bash
conda create -n blip_gpu python=3.11
conda activate blip_gpu
```
3. Install PyTorch with CUDA:
```bash
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```
4. Install other dependencies:
```bash
pip install -r requirements.txt
```

### Option 3: Use Current Setup (CPU Only)
The current setup will work with CPU, but BLIP-2 will be slower:
```bash
python main.py --blip2 --dual-screen --backend dshow --interval 5
```

## Testing GPU Support
After installing with GPU support, test with:
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU')"
```

## Performance Comparison
- **CPU**: BLIP-2 takes 10-30 seconds per caption
- **GPU**: BLIP-2 takes 2-5 seconds per caption
- **CPU**: BLIP takes 3-8 seconds per caption  
- **GPU**: BLIP takes 1-2 seconds per caption

## Current Status
Your system has:
- NVIDIA GTX 1650 (4GB VRAM)
- CUDA 12.9 drivers
- Python 3.14 (too new for CUDA PyTorch builds)

## Recommendation
Use Option 1 with Python 3.11 or 3.12 for best results.
