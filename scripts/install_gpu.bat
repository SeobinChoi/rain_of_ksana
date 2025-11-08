@echo off
echo 🚀 Installing GPU-enabled PyTorch for BLIP Camera Captioning
echo ============================================================

echo.
echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 2: Uninstalling existing PyTorch...
pip uninstall torch torchvision torchaudio -y

echo.
echo Step 3: Installing CUDA-enabled PyTorch...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo Step 4: Installing other dependencies...
pip install -r requirements.txt

echo.
echo Step 5: Testing GPU installation...
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('GPU name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU')"

echo.
echo ✅ Installation complete! You can now run BLIP-2 with GPU acceleration.
echo.
echo Test commands:
echo python main.py --blip2 --dual-screen --backend dshow --interval 5
echo.
pause
